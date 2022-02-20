import requests
import os
import xmltodict
import json
import logging
import datetime
import xml.etree.ElementTree as ET

# download
def run(app, url, path):
      
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
                        netCDFile.write(chunk)
            netCDFile.close()
            logging.info(str(datetime.datetime.now()) +
                    ' -  Download NETCD datasets Ok to ' + path)
            return True
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
def download(app, path, ncFiles, product):

      path, dirs, files = next(os.walk(path))
      ext = '.nc'

      logging.info(str(datetime.datetime.now()) + ' - ' +
              ' start downloading from ' + product + ' to ' + path)

      index_file = 1
      ncFiles.sort()
      for ncFile in ncFiles:
            # ----------------------------------------------
            # download netcd file from sentinel hub
            pathFile = path + '/' + product + "_" + str(index_file) + ext

            # download dataset
            run(app, ncFile, pathFile)
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
def getDatasets(app, url):

      try:
            # ----------------------------------------------
            # request HTTP GET data
            response = requests.get(url, verify=True, stream=True, timeout=120, auth=(app.config["S5_USERNAME"],
                                                                                    app.config["S5_PASSWORD"]))
            if (response.status_code == 200):
                  return parseXML(response.content), True, 200
            else:
                  logging.warning(str(datetime.datetime.now()) +
                        ' -  Status Code : ' + response.status_code + ' from ' + url)
                  response.raise_for_status()
                  return [], True, response.status_code
      except requests.ReadTimeout:
            logging.error(str(datetime.datetime.now()) +
                  ' -  Readtimeout from : ' + url)
            return [], True, requests.ReadTimeout


