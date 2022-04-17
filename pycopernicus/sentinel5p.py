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

# ----------------------------------------------------------------
# POST /sentinel5P 
@app.route('/pollution', methods=['POST'])
def sentinel5P():

    #test = False
    start = 0
    end = False

    response = {
        "status": [],
        "error": [],
        "links": []
    }

    product = getProduct(request.form['product'])

    bbox = (float(request.form['xmin']), float(request.form['ymin']),
            float(request.form['xmax']), float(request.form['ymax']))

    #if (test == True):
    #    print('product:' + product)
    #    pathFiles = '/Users/gzileni/Git/pyCopernicus/downloads/e1ca1af2-03ea-4912-b383-006e749ccfb1/L2__CO____/'
    #    send_ncfiles(app, pathFiles, product, bbox)
    #    return {
    #        'test': 'Ok'
    #    }
    #else:

    while end==False:
        # TODO: loop to page loading 
        url = 'https://' + app.config["S5_URL"] + '/dhus/search?start=' + str(start) + '&rows=100&q=' + app.config["S5_RANGE"] + \
            ' AND platformname:Sentinel-5 Precursor' + \
            ' AND producttype:' + product + \
            ' AND ' + getFootprint(bbox)

        # get url datasets
        ncFiles, error, status = getDatasets(
            app, url, app.config["S5_USERNAME"], app.config["S5_PASSWORD"])

        response["status"].append(status)
        response["error"].append(error)
        response["links"].append(ncFiles)

        logging.info(str(datetime.datetime.now()) + ' - get datasets from ' + url)

        if (len(ncFiles) > 0):
            # -----------------------------------------
            # create download folder if not exists
            pathFiles, rootPath = create_download_folder(app, product)
            # -----------------------------------------
            # download datasets
            download(app, pathFiles, ncFiles, product, '.nc',
                    app.config["S5_USERNAME"], app.config["S5_PASSWORD"])
            # -----------------------------------------
            # update postgis
            send_ncfiles(app, pathFiles, product, bbox)
            # -----------------------------------------
            # delete datasets
            delete_folder(pathFiles)
            os.rmdir(rootPath)
            
            start += 101
        else:
            end = True
    
    return response

# ----------------------------------------------------------------
# get geojson from intersect geometry
# GET /sentinel5p/<string:product>/<int:code>/<float:lat>/<float:lng>
@app.route('/pollution/<string:product>/<int:code>/<float:lat>/<float:lng>', methods=['GET'])
def sentinel5P_geojson(product, code, lat, lng):
    return get_GeoJSON(app, getProduct(product), code, lat, lng)


