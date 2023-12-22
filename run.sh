#!/bin/bash

source sc_venv_template/activate.sh 

# Open it in background as I want to control the servo after the camera is on
python real_time_with_labels.py --model=./mobilenet_v2.tflite --label=./coco_labels.txt --target="cell phone" &

# Run the servo control script. This messes up output, but it's fine for now
python ./ServoKitExample.py
