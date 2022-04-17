import json
import pathlib
from tabnanny import check
import os

from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *

import shapely.geometry
import xarray as xr
import geopandas
import dask
import logging
import datetime

shapely.speedups.disable()

from pycopernicus import app

file_checked = ''
sentinel5p_config = {}

# get configuration product
def getConfig(product):
     # read db parameters
    parent_folder = pathlib.Path(__file__).parent.absolute()
    path_config = str(parent_folder) + "/config/" + "sentinel5p.json"
    f = open(path_config)
    product_config = json.load(f)
    f.close()

    return product_config

# get engine database
def getEngine(app):
    url = "postgresql://" + app.config["USERNAME_PG"] + ":" + app.config["PASSWORD_PG"] + "@" + \
        app.config["POSTGRESQL"] + ":" + \
        str(app.config["PORT"]) + "/" + app.config["DATABASE"]
    engine = create_engine(url)
    return engine

# check integrity file and removed 
def check_integrity(path):
    global file_checked
    try: 
        for root, dirs, files in os.walk(path, topdown=False):
            files.sort()
            # check corrupted files
            for f in files:
                file_checked = os.path.join(root, f)
                datas = xr.open_dataset(file_checked,
                                          engine="netcdf4",
                                          group="PRODUCT",
                                          decode_times=True,
                                          decode_timedelta=True,
                                          decode_coords=True,
                                          parallel=True)
                msg = str(datetime.datetime.now()) + ' -  Check integrity file NETCD OK by ' + file_checked
                print(msg)
                logging.info(msg)
        
    except:
        msg = str(datetime.datetime.now()) + ' -  ERROR. check integrity to: ' + file_checked
        print(msg)
        logging.error(msg)
        os.remove(file_checked)

# update postgis
def send_ncfiles(app, path, product, bbox):

    config = getConfig(product)
    product_config = config[product]
    variables = product_config["variables"]

    # check integrity files
    check_integrity(path)

    with dask.config.set(**{'array.slicing.split_large_chunks': True}):
        try:
            datas = xr.open_mfdataset(path + "/*.nc",
                                    engine="netcdf4",
                                    group="PRODUCT",
                                    decode_times=True,
                                    decode_timedelta=True,
                                    decode_coords=True,
                                    parallel=True)

            # select quality data qa_value >= 0.75 
            datas_q = datas.where(datas.qa_value >= 0.75, drop=True)
            # https://xarray.pydata.org/en/stable/user-guide/io.html?highlight=_FillValue#scaling-and-type-conversions
            # The netCDF data types char, byte, short, int, float or real, and double are all acceptable
            datas_q['time_utc'] = datas_q['time_utc'].astype(str)
            datas_q['delta_time'] = datas_q['delta_time'].astype(str)

            for variable in variables:

                # add fields to dataframe
                datas_prod = datas_q[variable]

                datas_prod['time_utc'] = datas_q['time_utc']
                datas_prod['delta_time'] = datas_q['delta_time']
                datas_prod['platform'] = config["platform"]
                datas_prod['description'] = product_config["description"]
                datas_prod['created_at'] = datetime.datetime.now()
                datas_prod['ts'] = datetime.datetime.now().timestamp()

                # copy attributes to new dataframe's fields
                for attr in datas_prod.attrs:
                    datas_prod[attr] = datas_prod.attrs[attr]

                # get engine postgresql
                engine = getEngine(app)

                # create databrame
                pdataf = datas_prod.to_dataframe().dropna()
                s = geopandas.GeoSeries.from_xy(
                    pdataf.latitude, pdataf.longitude,
                    crs=app.config["S5_CRS"]).buffer(0.035, resolution=4, join_style=1)

                # create geometry from bbox to intersect dataframe
                p1 = shapely.geometry.box(*bbox, ccw=True)
                geodf_l = geopandas.GeoDataFrame(
                    geometry=geopandas.GeoSeries([p1]), crs=app.config["S5_CRS"])
                
                # ---------------------------------------------------------------
                # create dataframe with all dataframe's coordinates 
                geodf_r = geopandas.GeoDataFrame(
                    pdataf, geometry=s, crs=app.config["S5_CRS"])

                # update db to schema warning with all coordinates
                geodf = geopandas.sjoin(geodf_r, geodf_l)
                # update db
                print(geodf.head(5))
                geodf.to_postgis(product_config["table"],
                                engine,
                                schema=app.config["SCHEMA"],
                                if_exists="append",
                                chunksize=app.config["CHUNKSIZE"])
                msg = 'update postgis OK.'
                logging.info(msg)
                print(msg)
        except:
            logging.error('Error to open path ' + path)

# get geojson from postgis
def get_GeoJSON(app, product, code, lat, lng):
    config = getConfig(product)
    product_config = config[product]

    df = None
    # system reference
    crs = "EPSG:" + str(code)
    engine = getEngine(app)

    sql = "SELECT * FROM " + app.config["SCHEMA"] + "." + product_config["table"] + \
        " WHERE ST_Intersects('SRID=" + str(code) + \
        ";POINT(" + lng + " " + lat + ")'::geometry)"
    
    df = geopandas.read_postgis(
        sql,
        con=engine,
        geom_col="geometry",
        crs=crs)

    return df.to_json(na="drop", show_bbox=True)

# impot shapefile to postgis
def send_shape(app, shape, crs, table):
    gp = geopandas.read_file(shape).to_crs(crs=crs)
    pg_url = 'postgresql://' + app.config["USERNAME_PG"] + ':' + app.config["PASSWORD_PG"] + \
        '@' + app.config["POSTGRESQL"] + ':' + \
        str(app.config["PORT"]) + '/' + app.config["DATABASE"]
    engine = create_engine(pg_url)
    gp.to_postgis(table, engine, schema=app.config["SCHEMA"],
                  if_exists="replace", chunksize=app.config["CHUNKSIZE"])
            
