#!/bin/bash

. venv/bin/activate
export FLASK_APP=pycopernicus
export FLASK_ENV=production
flask run -p 5001 -h 0.0.0.0
