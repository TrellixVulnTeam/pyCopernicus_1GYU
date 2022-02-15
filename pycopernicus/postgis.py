import json
import pathlib

from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *

import shapely.geometry
import xarray as xr
import geopandas

from pycopernicus import app

# get configuration product
def getConfig(product):
     # read db parameters
    parent_folder = pathlib.Path(__file__).parent.absolute()
    path_config = str(parent_folder) + "/config/" + product + ".json"
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

# update postgis
def send_ncfiles(app, path, product, bbox):

    product_config = getConfig(product)

    variables = product_config["variables"]
    print(variables)

    print('--- update postgis from ', path)
    datas = xr.open_mfdataset(path + "/*.nc",
                              engine="netcdf4",
                              group="PRODUCT",
                              decode_times=True,
                              decode_timedelta=True,
                              decode_coords=True,
                              parallel=True)

    # select quality data over 0.75
    datas_q = datas.where(datas.qa_value >= 0.75, drop=True)
    # https://xarray.pydata.org/en/stable/user-guide/io.html?highlight=_FillValue#scaling-and-type-conversions
    # The netCDF data types char, byte, short, int, float or real, and double are all acceptable
    datas_q['time_utc'] = datas_q['time_utc'].astype(str)
    datas_q['delta_time'] = datas_q['delta_time'].astype(str)

    for variable in variables:

        # add fields
        datas_prod = datas_q[variable]
        datas_prod['time_utc'] = datas_q['time_utc']
        datas_prod['delta_time'] = datas_q['delta_time']
        datas_prod['platform'] = product_config["platform"]

        # copy attributes to dataframe
        for attr in datas_prod.attrs:
            datas_prod[attr] = datas_prod.attrs[attr]

        engine = getEngine(app)

        # create databrafe
        pdataf = datas_prod.to_dataframe().dropna()
        s = geopandas.GeoSeries.from_xy(
            pdataf.longitude, pdataf.latitude,
            crs=app.config["S5_CRS"])

        p1 = shapely.geometry.box(*bbox, ccw=True)
        geodf_l = geopandas.GeoDataFrame(
            geometry=geopandas.GeoSeries([p1]), crs=app.config["S5_CRS"])

        # update postgis
        geodf_r = geopandas.GeoDataFrame(
            pdataf, geometry=s, crs=app.config["S5_CRS"])

        geopandas.sjoin(geodf_r, geodf_l).to_postgis(
            product_config["table"],
            engine,
            schema=app.config["SCHEMA"],
            if_exists="replace",
            chunksize=app.config["CHUNKSIZE"])

    return variables

# get geojson from postgis
def get_GeoJSON(app, product, code, lat, lng):
    product_config = getConfig(product)

    df = None
    # system reference
    crs = "EPSG:" + str(code)
    engine = getEngine(app)

    sql = "SELECT * FROM" + app.config["SCHEMA"] + "." + product_config["table"] + \
        " WHERE ST_Intersects('SRID=" + str(code) + \
        ";POINT(" + lng + " " + lat + ")'::geometry)"
    print(sql)

    df = geopandas.read_postgis(
        sql,
        con=engine,
        geom_col="geometry",
        crs=crs)

    return df.to_json(na="drop", show_bbox=True)

# impot shapefile to postgis
def send_shape(app, shape, crs, table):
    print('imports to postgis table: ', table)
    gp = geopandas.read_file(shape).to_crs(crs=crs)
    pg_url = 'postgresql://' + app.config["USERNAME_PG"] + ':' + app.config["PASSWORD_PG"] + \
        '@' + app.config["POSTGRESQL"] + ':' + \
        str(app.config["PORT"]) + '/' + app.config["DATABASE"]
    engine = create_engine(pg_url)
    gp.to_postgis(table, engine, schema=app.config["SCHEMA"],
                  if_exists="replace", chunksize=app.config["CHUNKSIZE"])
