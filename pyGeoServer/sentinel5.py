import requests
import xmltodict
import json
import shapely.geometry
import os

from flask import flash, request
from pyGeoServer import app

import xarray as xr
import pandas as pd
import geopandas

from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
import json
import pathlib

headersXML = {'Content-Type': 'application/xml'}
headersJSON = {'Content-Type': 'application/json'}

download_path = os.path.abspath(
    os.getcwd()) + '/' + app.config['DOWNLOAD_FOLDER']

# get footprint to query
def getFootprint(bbox):
    polygon = shapely.geometry.box(*bbox, ccw=True)
    return 'footprint:"Intersects(' + str(polygon)  + ')"'

# get product to select dataset
def getProduct(product):
    if (product == 'CO'):
        return 'L2__CO____'
    elif (product == 'NO2'):
        return 'L2__NO2___'
    elif (product == 'SO2'):
        return 'L2__SO2___'
    elif (product == 'CH4'):
        return 'L2__CH4___'
    elif (product == 'HCHO'):
        return 'L2__HCHO__'
    elif (product == 'AER'):
        return 'L2__AER_AI'

# publish postgis table to GeoServer
def publish_postgis(table):
    print('--- publishing postgis table to geoserver: ', table)

    try:
        url = app.config["GEOSERVER"] + \
            '/rest/workspaces/' + \
            app.config["WORKSPACE"] + '/datastores/' + \
            app.config["WORKSPACE"] + 'featuretypes'
        payload = '<featureType><name>' + table + '</name></featureType>'
        geos_response = requests.post(url,
                                    auth=(app.config["USERNAME_GS"],
                                            app.config["PASSWORD_GS"]),
                                    data=payload,
                                    headers=headersXML)
        # curl - v - u admin: geoserver - X POST - H "Content-type: text/xml" - d "<featureType><name>lakes</name></featureType>" http: // localhost: 8080/geoserver/rest/workspaces/opengeo/datastores/pgstore/featuretypes
        return geos_response.content
    except requests.exceptions.HTTPError as err:
        return err

# publish netcdf store to geoserver
def publishNetCDF(file, product):

    print('--- publishing NETCDF file to geoserver: ', file)

    try: 
        store = "sentinel5P" + "_" + product
        payload = {
            store: {
                "name": file,
                "type": "NetCDF",
                "enabled": True,
                "_default": False,
                "workspace": {
                    "name": app.config["WORKSPACE"],
                },
                "url": "file:" + download_path + "\/" + file
            }
        }
        url = app.config["GEOSERVER"] + '/rest/workspaces/' + app.config["WORKSPACE"]
        geos_response = requests.post(url,
                                      auth=(app.config["USERNAME_GS"],
                                            app.config["PASSWORD_GS"]),
                                      data=payload,
                                      headers=headersJSON)
        return geos_response.content
    except requests.exceptions.HTTPError as err:
        return err

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
def getEngine():
    url = "postgresql://" + app.config["USERNAME_PG"] + ":" + app.config["PASSWORD_PG"] + "@" + \
        app.config["POSTGRESQL"] + ":" + \
        str(app.config["PORT"]) + "/" + app.config["DATABASE"]
    engine = create_engine(url)
    return engine

# update postgis
def update_postgis(path, product, bbox):

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

        engine = getEngine()

        # create databrafe
        pdataf = datas_prod.to_dataframe().dropna()
        s = geopandas.GeoSeries.from_xy(
            pdataf.longitude, pdataf.latitude, 
            crs=app.config["S5_CRS"])

        p1 = shapely.geometry.box(*bbox, ccw=True)
        geodf_l = geopandas.GeoDataFrame(geometry=geopandas.GeoSeries([p1]), crs=app.config["S5_CRS"])

        # update postgis
        geodf_r = geopandas.GeoDataFrame(
            pdataf, geometry=s, crs=app.config["S5_CRS"])
            
        geopandas.sjoin(geodf_r, geodf_l).to_postgis(
                product_config["table"],
                engine,
                schema=app.config["SCHEMA"],
                if_exists="replace",
                chunksize=app.config["CHUNKSIZE"])

        publish_postgis(variable)

# create list's url download datasets from sentinel hub
def getDatasetUrls(url):

    print("--- reading url datasets")
    # ----------------------------------------------
    # request HTTP GET data
    response = requests.get(url, timeout=120, auth=(app.config["S5_USERNAME"],
                                                    app.config["S5_PASSWORD"]))

    if (response.status_code == 200):
        # ----------------------------------------------
        # convert xml to json
        xpars = xmltodict.parse(response.text)
        jsonResponse = json.dumps(xpars)
        jsonObj = json.loads(jsonResponse)

        entries = []

        # ----------------------------------------------
        # get links to download NETCDFiles
        try:
            entries = jsonObj["feed"]["entry"]
        except:
            entries = []

        if (len(entries) > 0):
            ncFiles = []
            for entry in entries:
                ncFiles.append(entry["link"][0]["@href"])
            return ncFiles, False, 200
        else:
            return [], False, 200
    else:
        print('Status Code: ', response.status_code)
        response.raise_for_status()
        return [], True, response.status_code

# download 
def run_download(url, path):
    print("--- download: " + url)

    netCDFile = open(path, "wb")

    # get .nc files from datahub if don't exist
    fileNC = requests.get(url, 
                          auth=(app.config["S5_USERNAME"],
                                app.config["S5_PASSWORD"]),
                          stream=True)
    total_size = int(fileNC.headers.get('content-length'))
    chunks = 0
    for chunk in fileNC.iter_content(chunk_size=app.config["CHUNKSIZE"]):
        if chunk:
            chunks += 1
            downloaded = chunks * app.config["CHUNKSIZE"]
            # An approximation as the chunks don't have to be 512 bytes
            progress = int((downloaded/total_size)*100)
            print("-> downloading: " +
                    str(progress) + "%", end='')
            print('\r', end='')
            netCDFile.write(chunk)
    netCDFile.close()

# delete file downloaded
def delete_downloads(paths):
    for file in paths:
        os.remove(file)
# ----------------------------------------------------------------
# download file .nc
def download(ncFiles, product, bbox):

    files_downloaded = []
    
    # create download folder if not exists
    if (not os.path.isdir(download_path)):
        os.mkdir(download_path)

    path, dirs, files = next(os.walk(download_path))
    ext = '.nc'
    
    print('--- downloading ' + str(len(ncFiles)) + ' files.')

    # index_file = len(files) + 1
    index_file = 1
    ncFiles.sort()
    for ncFile in ncFiles:
        # ----------------------------------------------
        # download netcd file from sentinel hub
        pathFile = download_path + '/' + product + "_" + str(index_file) + ext
        files_downloaded.append(pathFile)
        # download dataset
        # run_download(ncFile, pathFile)
        index_file += 1

    #update postgis
    n = update_postgis(download_path, product, bbox)
    # delete files 
    # delete_downloads(files_downloaded)

@app.route('/sentinel5p', methods=['POST'])
def sentinel5P():

    response = {
        "status": "",
        "error": "",
        "links": []
    }

    bbox = [float(request.form['xmin']), float(request.form['ymin']), float(request.form['xmax']), float(request.form['ymax'])]
    product = getProduct(request.form['product'])

    url = 'https://' + app.config["S5_URL"] + '/dhus/search?start=0&rows=100&q=' + app.config["S5_RANGE"] + \
        ' AND platformname:Sentinel-5 Precursor' + \
        ' AND producttype:' + product + \
        ' AND ' + getFootprint(bbox)
    
    print('*****************************')
    print(url)
    print('*****************************\n')

    ncFiles, error, status = getDatasetUrls(url)

    response["status"] = status
    response["error"] = error
    response["links"] = ncFiles

    if (len(ncFiles) > 0):
        download(ncFiles, product, bbox)
        
    return response

# get geojson from intersect geometry
@app.route('/sentinel5p/<string:product>/<int:code>/<float:lat>/<float:lng>/<float:distance>')
def index(product, code, lat, lng, distance):

    product_config = getConfig(product)

    df = None
    # system reference
    crs = "EPSG:" + str(code)
    engine = getEngine()

    sql = "SELECT * FROM" + app.config["SCHEMA"] + "." + product_config["table"] + " WHERE ST_Intersects('SRID=" + str(code) + ";POINT(" + lng + " " + lat + ")'::geometry)"
    print(sql)
    df = geopandas.read_postgis(
        sql, 
        con=engine, 
        geom_col="geometry", 
        crs=crs)

    return df.to_json(na="drop", show_bbox=True)

    

