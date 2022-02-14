
def create_shp_datastore(self, path, workspace=None, store_name=None):
      '''
        Create the datastore for shapefile
        '''
       if path is None:
            raise Exception('You must provide a full path to shapefile')

        if workspace is None:
            workspace = 'default'

        if store_name is None:
            store_name = os.path.basename(path)
            f = store_name.split('.')
            if len(f) > 0:
                store_name = f[0]

        file = path if path.startswith("file:") else "file:{}".format(path)
        data = '<dataStore><name>{0}</name><connectionParameters><url>{1}</database></connectionParameters></dataStore>'.format(
            store_name, file)

        url = '{0}/rest/workspaces/{1}/datastores'.format(
            self.service_url, workspace)

        print(data, url, 'data,url')
        headers = {"content-type": "text/xml"}

        r = requests.post(url, data, auth=(
            self.username, self.password), headers=headers)

        print(r.status_code, r.content)


def data_upload(self, content_type='application/xml'):
    '''
    Upload the data to the geoserver REST service
    '''
    obj = UploadData(self, name, workspace)
    href = urlparse(obj.href)
    netloc = urlparse(self.service_url).netloc
    rest_url = href._replace(netloc=netloc).geturl()
    data = obj.message()

    headers = {
        "Content-type": content_type,
        "Accept": content_type
    }

    resp = requests(
        rest_url, method=obj.save_method.lower(), data=data, headers=headers)

    if resp.status_code not in (200, 201):
        raise FailedRequestError('Failed to save to Geoserver catalog: {}, {}'.format(
            resp.status_code, resp.text))

    self._cache.clear()
    return resp



class GeoTIFF:
    def __init__(self, geoserver, url, headers):
        self.url = url,
        self.headers = headers,

    @property
    def upload(self):
        url = 'file:data/{0}/{1}/{1}.geotiff'.format(
            self.geoserver.workspace, file_name)

        headers = {content_type = "application/xml"}

        with open(path, 'rb') as f:
            r = request.post(url, data=f.read(), headers=headers)



    def create_geotiff_coveragestore(self, path=None, name=None,  workspace=None, upload=True, overwrite=False):
        '''
        The path referes as path to the coverage
        The name referes as name of the coveragestore
        By default it will upload the data to the server. If you don't want to upload the data to the server, simply make upload=False
        '''
        if workspace is None:
            workspace = 'default'

        if path is None:
            raise Exception("You must provide a full path to the data")

        if name is None:
            name = os.path.basename(path)
            f = name.split(".")
            if len(f) > 0:
                name = f[0]

        data = '<coverageStore><name>{0}</name><url>file://{1}</url></coverageStore>'.format(
            name, path)

        headers = {"content-type": "text/xml"}

        try:
            r = None
            if upload:
                headers = {"content-type": 'image/tiff'}
                url = '{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}'.format(
                    self.service_url, workspace, name, 'geotiff')

                with open(path, 'rb') as f:
                    r = requests.put(url, data=f.read(), auth=(
                        self.username, self.password), headers=headers)

                if r.status_code in [200, 201]:
                    return "Geotiff coveragestore created/updated successfully"

                else:
                    raise Exception('Geotiff coveragestore can not be created')

            if overwrite:
                url = '{0}/rest/workspaces/{1}/coveragestores/{2}'.format(
                    self.service_url, workspace, name)
                r = requests.put(url, data, auth=(
                    self.username, self.password), headers=headers)

            else:
                url = '{0}/rest/workspaces/{1}/coveragestores'.format(
                    self.service_url, workspace)
                r = requests.post(url, data, auth=(
                    self.username, self.password), headers=headers)

                print(r.content, r.status_code)

            if r.status_code in [200, 201]:
                return "Geotiff coveragestore created/updated successfully"

            else:
                raise Exception('Geotiff coveragestore can not be created')

        except Exception as e:
            return "Error create_geotiff_coveragestore: {}".format(e)
