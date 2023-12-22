#!/bin/bash

source sc_venv_template/activate.sh 

gunicorn --threads 2 --workers 1 --bind 0.0.0.0:5000 app:app