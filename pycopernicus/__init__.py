from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('./config/pycopernicus.cfg', silent=True)

import pycopernicus.sentinel5p
import pycopernicus.imports