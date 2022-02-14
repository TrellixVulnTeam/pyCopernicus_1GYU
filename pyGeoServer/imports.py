import os
import geopandas
import zipfile
import requests

from flask import flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine

from pyGeoServer import app 

uploads_path = os.path.abspath(os.getcwd()) + '/' + app.config['UPLOAD_FOLDER']
headersXML = {'Content-Type': 'application/xml'}
headersJSON = {'Content-Type': 'application/json'}

# publish layer to geoserver
def publish(layer):
    print('publishing layer: ', layer)

    try:
        payload = '<featureType><name>' + layer + '</name></featureType>'
        geos_response = requests.post(app.config["GEOSERVER"] + '/rest/workspaces/' + app.config["WORKSPACE"] + '/datastores/' + app.config["DATASTORE"] + '/featuretypes',
                                      auth=(app.config["USERNAME_GS"],
                                            app.config["PASSWORD_GS"]), 
                                      data=payload,
                                      headers=headersXML)
        if (geos_response.status_code == 200 or geos_response.status_code == 201):
            print(geos_response.text)

    except requests.exceptions.HTTPError as err:
        print(err)

# impot shapefile to postgis
def imports(shape, crs, table):
    print('imports to postgis table: ', table)
    gp = geopandas.read_file(shape).to_crs(crs=crs)
    pg_url = 'postgresql://' + app.config["USERNAME_PG"] + ':' + app.config["PASSWORD_PG"] + \
        '@' + app.config["POSTGRESQL"] + ':' + \
        str(app.config["PORT"]) + '/' + app.config["DATABASE"]
    engine = create_engine(pg_url)
    gp.to_postgis(table, engine, schema=app.config["SCHEMA"], if_exists="replace", chunksize=app.config["CHUNKSIZE"])

# check file allowed to upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def unZip(filezip, path):
    with zipfile.ZipFile(filezip, 'r') as zip_ref:
        extracted = zip_ref.namelist()
        zip_ref.extractall(path)
    return os.path.join(path, extracted[0])

# POST /imports
@app.route('/imports', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # create uploads folder if not exists
            if (not os.path.isdir(uploads_path)):
                os.mkdir(uploads_path)
            # save file
            shapefileZipped = os.path.join(uploads_path, filename)
            file.save(shapefileZipped)
            pathShape = unZip(shapefileZipped, uploads_path)
            # imports to postgres
            imports(pathShape, request.form['crs'], request.form['layer'])
            # publish layer
            publish(request.form['layer'])
            # send response to clients
            return redirect(url_for('download_file', name=filename))

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(uploads_path, name)