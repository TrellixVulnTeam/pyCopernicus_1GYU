from flask import Flask
app = Flask(__name__)

app.config.from_pyfile('./config/pyGeoServer.cfg', silent=True)

import pyGeoServer.imports
import pyGeoServer.sentinel5