import shapely.geometry

from flask import request
from .datasets import download, getDatasets, delete_datasets
from .geoserver import publish_postgis
from .postgis import send_ncfiles, get_GeoJSON

from pycopernicus import app

# get footprint to query
def getFootprint(bbox):
    polygon = shapely.geometry.box(*bbox, ccw=True)
    return 'footprint:"Intersects(' + str(polygon) + ')"'

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
    
    ncFiles, error, status = getDatasets(app, url)

    response["status"] = status
    response["error"] = error
    response["links"] = ncFiles
    
    if (len(ncFiles) > 0):
        path = download(app, ncFiles, product)
        vars = send_ncfiles(app, path, product, bbox)
        response["geoserver"] = publish_postgis(app, vars)
        delete_datasets(path)
        
    return response

# ----------------------------------------------------------------
# get geojson from intersect geometry
# GET /sentinel5p/<string:product>/<int:code>/<float:lat>/<float:lng>
@app.route('/sentinel5p/<string:product>/<int:code>/<float:lat>/<float:lng>')
def index(product, code, lat, lng):
    return get_GeoJSON(app, getProduct(product), code, lat, lng)


