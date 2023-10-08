#!/bin/sh

source sc_venv_template/activate.sh
python real_time_with_labels.py --model=./mobilenet_v2.tflite --label=./coco_labels.txt
