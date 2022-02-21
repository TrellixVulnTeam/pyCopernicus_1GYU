from flask import request
from .functions import delete_folder, create_download_folder
from .datasets import download, getDatasets, getFootprint
from .postgis import send_ncfiles, get_GeoJSON

from pycopernicus import app

import logging 
import datetime
import os

# get product to select dataset
def getProduct(product):
    if (product == 'NDVI1'):
        return 'SY_2_VG1___'
    elif (product == 'NDVI10'):
        return 'SY_2_V10___'

# ----------------------------------------------------------------
# POST /sentinel3 
@app.route('/vegetation', methods=['POST'])
def sentinel3():

    response = {
        "status": "",
        "error": "",
        "links": []
    }

    bbox = [float(request.form['ymin']), float(request.form['xmin']), float(request.form['ymax']), float(request.form['xmax'])]
    
    product = getProduct(request.form['product'])

    url = 'https://' + app.config["S3_URL"] + '/dhus/search?start=0&rows=100&q=' + app.config["S3_RANGE"] + \
        ' AND platformname:Sentinel-3' + \
        ' AND producttype:' + product + \
        ' AND ' + getFootprint(bbox)
    
    # get url datasets
    ncFiles, error, status = getDatasets(
        app, url, app.config["S3_USERNAME"], app.config["S3_PASSWORD"])

    response["status"] = status
    response["error"] = error
    response["links"] = ncFiles

    logging.info(str(datetime.datetime.now()) + ' - get datasets from ' + url)

    print(ncFiles)
    
    if (len(ncFiles) > 0):
        # -----------------------------------------
        # create download folder if not exists
        pathFiles, rootPath = create_download_folder(app, product)
        # -----------------------------------------
        # download datasets
        download(app, 
                 pathFiles, 
                 ncFiles, 
                 product, 
                 '.zip',
                 app.config["S3_USERNAME"], 
                 app.config["S3_PASSWORD"])
        # -----------------------------------------
        # update postgis
        # send_ncfiles(app, pathFiles, product, bbox)
        # -----------------------------------------
        # delete datasets
        # delete_folder(pathFiles)
        # os.rmdir(rootPath)
        
    return response

@app.route('/vegetation/<string:product>/<int:code>/<float:lat>/<float:lng>', methods=['GET'])
def sentinel3_geojson(product, code, lat, lng):
    return get_GeoJSON(app, getProduct(product), code, lat, lng)


