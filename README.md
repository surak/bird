# Bird detector

This is a toy project, where I join a bunch of different technologies to better follow birds!

Most of the time in this project has been trying to make the Arducam 16mp Autofocus camera work. Now that I know, it's easier. I should have used the Picamera2 and Libcamera from the beginning, and left the old method of grabbing images with default OpenCV behind.

## Hardware requirements: 

- An autofocus camera (it's half the price of the Raspberry's Quality camera and is a trillion times better) https://www.arducam.com/product/imx519-autofocus-camera-module-for-raspberry-pi-arducam-b0371/
- The Pan-Tilt platform: https://www.arducam.com/product/arducam-pan-tilt-platform-for-raspberry-pi-camera-2-dof-bracket-kit-with-digital-servos-and-ptz-control-broad/
- A raspberry Pi 4 with more at least 4gb of ram

## Software requirements:

- Stefan's virtual env manager: https://gitlab.jsc.fz-juelich.de/kesselheim1/sc_venv_template - symlink the requirements from here to it, and cleanup modules.txt
- The drivers for the camera: https://www.arducam.com/docs/cameras-for-raspberry-pi/raspberry-pi-libcamera-guide/how-to-use-arducam-16mp-camera-on-rapberry-pi/
- libcamera from Arducam, for autofocus (same page as arducam drivers)

Camera driver install
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
- Check run.sh

## TODO

- A full pipeline for PyTorch's models to be trained in a supercomputer, and quantized and reduced to run at a decent performance on the Raspberry Pi.
