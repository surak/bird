#!/usr/bin/python3

# Copyright (c) 2022 Raspberry Pi Ltd
# Author: Alasdair Allan <alasdair@raspberrypi.com>
# SPDX-License-Identifier: BSD-3-Clause

# A TensorFlow Lite example for Picamera2 on Raspberry Pi OS Bullseye
#
# Install necessary dependences before starting,
#
# $ sudo apt update
# $ sudo apt install build-essentials
# $ sudo apt install libatlas-base-dev
# $ sudo apt install python3-pip
# $ pip3 install tflite-runtime
# $ pip3 install opencv-python==4.4.0.46
# $ pip3 install pillow
# $ pip3 install numpy
#
# and run from the command line,
#
# $ python3 real_time_with_labels.py --model mobilenet_v2.tflite --label coco_labels.txt

import argparse
import os
import sys
import logging
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image, ImageDraw, ImageFont
import adafruit_servokit

from picamera2 import MappedArray, Picamera2, Preview

from ServoKit import *


servoKit = ServoKit(2)

normalSize = (1280, 960)
lowresSize = (640, 480)
rectangles = []

def ReadLabelFile(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret

def DrawRectangles(request):
    with MappedArray(request, "main") as m:
        for rect in rectangles:
            # print(rect)
            rect_start = (int(rect[0] * 2) - 5, int(rect[1] * 2) - 5)
            rect_end = (int(rect[2] * 2) + 5, int(rect[3] * 2) + 5)
            logging.info("rect_start:", rect_start, "rect_end:",rect_end)
            cv2.rectangle(m.array, rect_start, rect_end, (0, 255, 0, 0))
            center = (
                rect_start[0]+int((rect_end[0]-rect_start[0])/2),
                rect_end[1]+int((rect_start[1]-rect_end[1])/2)
            )
            logging.info("Center of the rectangle",center)
            cv2.circle(m.array, center, radius=5, color=(255,0,0), thickness=20)
            if rect[4] == "person":
                defineMovement(center)

            if len(rect) >= 5:
                text = rect[4]+": {:.2f}".format(rect[5]*100)+"%"
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(m.array, text, (int(rect[0] * 2) + 10, int(rect[1] * 2) - 12), font, 2, (255, 255, 255), 4, cv2.LINE_AA)

def defineMovement(center):
    # If something is found on the first or last quarter of the image, try to bring it to the center
    if(center[0]<(normalSize[0]/4)):
        print("moving right")
        MoveCamera(-2,0)
    if(center[0]>(normalSize[0]-(normalSize[0]/4))):
        print("moving left")
        MoveCamera(2,0)
    if(center[1]<(normalSize[1]/4)):
        print("moving up")
        MoveCamera(0,1)
    if(center[1]>(normalSize[1]-(normalSize[1]/4))):
        print("moving down")
        MoveCamera(0,-1)


def MoveCamera(deltaX,deltaY):
    # Motor 0 vertical (0 is looking down )
    # Motor 1 horizontal (0 is looking left)
    # Setangle goes between 0 and 180
    #print("Move camera: center:", center)
    servoKit.setAngle(ServoKit.x, servoKit.getAngle(ServoKit.x)+deltaX)
    servoKit.setAngle(ServoKit.y, servoKit.getAngle(ServoKit.y)+deltaY)



def InferenceTensorFlow(image, model, output, labels=None):
    global rectangles

    interpreter = tflite.Interpreter(model_path=model, num_threads=4)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    floating_model = False
    if input_details[0]['dtype'] == np.float32:
        floating_model = True

    rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    initial_h, initial_w, channels = rgb.shape

    picture = cv2.resize(rgb, (width, height))

    input_data = np.expand_dims(picture, axis=0)
    if floating_model:
        input_data = (np.float32(input_data) - 127.5) / 127.5

    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    detected_boxes = interpreter.get_tensor(output_details[0]['index'])
    detected_classes = interpreter.get_tensor(output_details[1]['index'])
    detected_scores = interpreter.get_tensor(output_details[2]['index'])
    num_boxes = interpreter.get_tensor(output_details[3]['index'])

    rectangles = []
    for i in range(int(num_boxes)):
        top, left, bottom, right = detected_boxes[0][i]
        classId = int(detected_classes[0][i])
        score = detected_scores[0][i]
        if score > 0.5:
            xmin = left * initial_w
            ymin = bottom * initial_h
            xmax = right * initial_w
            ymax = top * initial_h
            box = [xmin, ymin, xmax, ymax]
            rectangles.append(box)
            if labels:
                # print(labels[classId], 'score = ', score)
                rectangles[-1].append(labels[classId])
                rectangles[-1].append(score)
            else:
                pass
                # print('score = ', score)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='Path of the detection model.', required=True)
    parser.add_argument('--label', help='Path of the labels file.')
    parser.add_argument('--output', help='File path of the output image.')
    args = parser.parse_args()

    if (args.output):
        output_file = args.output
    else:
        output_file = 'out.jpg'

    if (args.label):
        labels = ReadLabelFile(args.label)
    else:
        labels = None

    picam2 = Picamera2()
    picam2.start_preview(Preview.QTGL)
    config = picam2.create_preview_configuration(main={"size": normalSize},
                                          lores={"size": lowresSize, "format": "YUV420"})
    picam2.configure(config)
    picam2.set_controls({"AfTrigger": 1})

    stride = picam2.stream_configuration("lores")["stride"]
    picam2.post_callback = DrawRectangles

    picam2.start()
    

    servoKit.setAngle(1, 150)
    servoKit.setAngle(0, 150)
    print("Init code:", servoKit.getAngle(1), servoKit.getAngle(0))
    global pos
    pos=(servoKit.getAngle(1), servoKit.getAngle(0))
    while True:
        buffer = picam2.capture_buffer("lores")
        grey = buffer[:stride * lowresSize[1]].reshape((lowresSize[1], stride))
        result = InferenceTensorFlow(grey, args.model, output_file, labels)


if __name__ == '__main__':
    main()
