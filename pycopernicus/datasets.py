import requests
import os
import xmltodict
import json

# download
def run(app, url, path):
      print("--- download: " + url)

      netCDFile = open(path, "wb")

      try:
            # get .nc files from datahub if don't exist
            fileNC = requests.get(url,
                                  timeout=120,
                                  verify=True,
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
            return True
      except requests.ReadTimeout:
            return False

# ----------------------------------------------------------------
# download file .nc
def download(app, path, ncFiles, product):

      path, dirs, files = next(os.walk(path))
      ext = '.nc'

      print('--- downloading ' + str(len(ncFiles)) + ' files.')

      # index_file = len(files) + 1
      index_file = 1
      ncFiles.sort()
      for ncFile in ncFiles:
            # ----------------------------------------------
            # download netcd file from sentinel hub
            pathFile = path + '/' + product + "_" + str(index_file) + ext
            # download dataset
            run(app, ncFile, pathFile)
            index_file += 1

# create list's url download datasets from sentinel hub
def getDatasets(app, url):

      print('*****************************')
      print(url)
      print('*****************************\n')
      print("--- reading url datasets")

      try:
            # ----------------------------------------------
            # request HTTP GET data
            response = requests.get(url, verify=True, stream=True, timeout=120, auth=(app.config["S5_USERNAME"],
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
      except requests.ReadTimeout:
            return [], True, response.status_code

# delete file downloaded
def delete_datasets(paths):
    for file in paths:
        os.remove(file)
