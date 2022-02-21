import requests
import os
import logging
import datetime
import xml.etree.ElementTree as ET
import shapely.geometry
import zipfile

shapely.speedups.disable()

# get footprint to query
def getFootprint(bbox):
    polygon = shapely.geometry.box(*bbox, ccw=True)
    return 'footprint:"Intersects(' + str(polygon) + ')"'

# download
def run(app, url, path, username, password, unzip, product, index):
      
      netCDFile = open(path, "wb")
      try:
            # get .nc files from datahub if don't exist
            fileNC = requests.get(url,
                                  timeout=120,
                                  verify=True,
                                  auth=(username,
                                        password),
                                  stream=True)
            for chunk in fileNC.iter_content(chunk_size=app.config["CHUNKSIZE"]):
                  # An approximation as the chunks don't have to be 512 bytes
                  netCDFile.write(chunk)
            netCDFile.close()

            if (unzip):
                  dirUnzip = str(path) + '/' + product + "_" + str(index)
                  # unzip files
                  with zipfile.ZipFile(path, 'r') as zip_ref:
                        zip_ref.extractall(dirUnzip)
                  return dirUnzip
            else:
                  logging.info(str(datetime.datetime.now()) +
                        ' -  Download NETCD datasets Ok to ' + path)
                  return path
      except requests.ReadTimeout:
            logging.error(str(datetime.datetime.now()) +
                        ' -  Readtimeout from : ' + url)
            return False
      except:
            logging.error(str(datetime.datetime.now()) +
                        ' -  errror')
            return False

# ----------------------------------------------------------------
# download file .nc
def download(app, path, ncFiles, product, ext, username, password):

      path, dirs, files = next(os.walk(path))
      
      logging.info(str(datetime.datetime.now()) + ' - ' +
              ' start downloading from ' + product + ' to ' + path)

      index_file = 1
      ncFiles.sort()
      for ncFile in ncFiles:
            # ----------------------------------------------
            # download netcd file from sentinel hub
            pathFile = path + '/' + product + "_" + str(index_file) + ext

            # download dataset
            run(app, ncFile, pathFile, username, password, ext == '.zip', product, index_file)
            index_file += 1

# parse xml response from copernicus
def parseXML(xmlfile):

      # create element tree object
      tree = ET.fromstring(xmlfile)

      # get root element
      root = tree.iter('*')
      
      # create empty list for news items
      linkitems = []

      # iterate news items
      for child in root:
            if ('link' in child.tag):
                  if ('href' in child.attrib):
                        for item in child.attrib:
                              if ('$value' in child.attrib[item] and not 'Quicklook' in child.attrib[item]):
                                    linkitems.append(child.attrib[item])

      return linkitems

# create list's url download datasets from sentinel hub
def getDatasets(app, url, username, password):

      try:
            # ----------------------------------------------
            # request HTTP GET data
            response = requests.get(url, verify=True, stream=True, timeout=120, auth=(username, password))
            if (response.status_code == 200):
                  return parseXML(response.content), True, 200
            else:
                  logging.warning(str(datetime.datetime.now()) +
                        ' -  Status Code : ' + str(response.status_code) + ' from ' + url)
                  response.raise_for_status()
                  return [], True, response.status_code
      except requests.ReadTimeout:
            logging.error(str(datetime.datetime.now()) +
                  ' -  Readtimeout from : ' + url)
            return [], True, requests.ReadTimeout


