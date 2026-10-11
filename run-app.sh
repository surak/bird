#!/bin/bash

source .venv/bin/activate

gunicorn --threads 2 --workers 1 --bind 0.0.0.0:5000 app:app --reload