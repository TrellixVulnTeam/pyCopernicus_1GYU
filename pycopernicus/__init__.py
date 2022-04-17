import logging

from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('./config/pycopernicus.cfg', silent=True)

logging.basicConfig(filename='./logs/sentinel.log',
                    encoding='utf-8', level=logging.DEBUG)

import pycopernicus.sentinel5p
import pycopernicus.sentinel3
import pycopernicus.imports
