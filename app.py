#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, request
from servo import *

# The original example created a base_camera, with different "drivers" for different cameras.
# Check it at https://github.com/miguelgrinberg/flask-video-streaming
from camera import Camera

app = Flask(__name__)

servo=Servo()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Strube's birds"""
    if request.method == 'POST':
        if 'up' in request.form:
            servo.up()
        elif 'down' in request.form:
            servo.down()
        elif 'left' in request.form:
            servo.left()
        elif 'right' in request.form:
            servo.right()
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
