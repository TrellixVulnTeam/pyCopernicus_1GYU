import requests

headersXML = {'Content-Type': 'application/xml'}
headersJSON = {'Content-Type': 'application/json'}

# publish shape files
def publish_shape(app, layer):
    print('publishing shapefile to layer: ', layer)

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

# publish postgis table to GeoServer
def publish_postgis(app, tables):

    for table in tables:
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
def publish_netcdf(app, path, file, product):

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
                "url": "file:" + path + "\/" + file
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