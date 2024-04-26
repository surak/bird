# Bird detector

This is a toy project, where I join a bunch of different technologies to better follow birds!

Most of the time in this project has been trying to make the Arducam 16mp Autofocus camera work. Now that I know, it's easier. I should have used the Picamera2 and Libcamera from the beginning, and left the old method of grabbing images with default OpenCV behind.

## Hardware requirements: 

- An autofocus camera (it's half the price of the Raspberry's Quality camera and is a trillion times better) https://www.arducam.com/product/imx519-autofocus-camera-module-for-raspberry-pi-arducam-b0371/
- The Pan-Tilt platform: https://www.arducam.com/product/arducam-pan-tilt-platform-for-raspberry-pi-camera-2-dof-bracket-kit-with-digital-servos-and-ptz-control-broad/
- A raspberry Pi 4 with more at least 4gb of ram

## Software requirements:

- python3-opencv as a debian package. As of December 2023, the python-opencv from pip will fail because of the missing QT stuff.
- Stefan's virtual env manager: https://gitlab.jsc.fz-juelich.de/kesselheim1/sc_venv_template - symlink the requirements from here to it, and cleanup modules.txt
- The documentation of the Arducam 16mp: https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/Quick-Start-Guide/#software-guide-for-imx519-autofocus-camera


TL;DR:
```
cd ~
wget -O install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
chmod +x ./install_pivariety_pkgs.sh
sudo ./install_pivariety_pkgs.sh -p libcamera
sudo ./install_pivariety_pkgs.sh -p libcamera_apps
sudo apt install python3-opencv
```


### Already on requirements.txt: 
- Adafruit ServoKit https://pypi.org/project/adafruit-circuitpython-servokit/
- tflite_runtime from pip.

## Running

- As of today, I'm using mobilenet_v2 heavily quantized, which gave me 30fps, compared to 1.6fps on Yolo7 with ONNX.
- run_app.sh calls uvicorn on port 5000

## TODO

- There's something going on with the rectangles and the detection. I am not sure if it's calculating on the small buffer and going to the big one. 
    - I think it's because the inference buffer and the display buffer have to be multiples of each other, but I'm not sure.
- Fine-tune on birds
- A full pipeline for PyTorch's models to be trained in a supercomputer, and quantized and reduced to run at a decent performance on the Raspberry Pi.
- Fix the autofocus on the Pi5. It's not working, and I'm not sure why.

## Acknowledgments:

- The mjpeg server with gunicorn comes from https://github.com/miguelgrinberg/flask-video-streaming