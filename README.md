# Bird detector

This is a toy project, where I join a bunch of different technologies to better follow birds!

Most of the time in this project has been trying to make the Arducam 16mp Autofocus camera work. Now that I know, it's easier. I should have used the Picamera2 and Libcamera from the beginning, and left the old method of grabbing images with default OpenCV behind.

## Hardware requirements: 

- An autofocus camera (it's half the price of the Raspberry's Quality camera and is a trillion times better) https://www.arducam.com/product/imx519-autofocus-camera-module-for-raspberry-pi-arducam-b0371/
- The Pan-Tilt platform: https://www.arducam.com/product/arducam-pan-tilt-platform-for-raspberry-pi-camera-2-dof-bracket-kit-with-digital-servos-and-ptz-control-broad/
- A raspberry Pi 4 with more at least 4gb of ram

## Software requirements:

- The camera/opencv stack comes from Debian packages (the pip opencv wheels break on the Pi); uv manages everything else in `.venv`. Every system dependency - including uv itself, git and the Arducam driver bits - is in the copy-paste block under "TL;DR" below.
- Trap worth knowing: the venv must be created with `--system-site-packages` off the **system** Python *before* `uv sync`. If uv creates the venv itself (any stray `uv sync`/`uv run`), the flag is off and cv2/picamera2 raise `ModuleNotFoundError` although the system has them.
- The documentation of the Arducam 16mp: https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/Quick-Start-Guide/#software-guide-for-imx519-autofocus-camera


## TL;DR — one copy-paste on a clean Raspberry Pi

From flashing the SD card to serving video and steering the rig. Safe to re-run on a
partly set up system (it is idempotent and rebuilds the Python env from scratch).

```sh
# --- 1. System packages: camera/opencv stack (apt only!), git, curl ---
sudo apt update
sudo apt install -y git curl python3-picamera2 python3-libcamera python3-opencv python3-numpy python3-pil

# --- 2. Arducam IMX519 support. Only needed on older images; on current
#     Raspberry Pi OS the stock libcamera already drives the IMX519. ---
cd ~
curl -fsSL -o install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh
chmod +x ./install_pivariety_pkgs.sh
sudo ./install_pivariety_pkgs.sh -p libcamera
sudo ./install_pivariety_pkgs.sh -p libcamera_apps

# --- 3. I2C for the pan-tilt servos (saves it for every boot, modprobe makes it live now) ---
sudo raspi-config nonint do_i2c 0
sudo modprobe i2c-dev

# --- 4. uv itself ---
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# --- 5. The code ---
mkdir -p ~/Devel
cd ~/Devel/bird 2>/dev/null || { cd ~/Devel && git clone https://github.com/surak/bird.git && cd bird; }
git pull --ff-only 2>/dev/null || true

# --- 6. Python environment. Recreate the venv WITH --system-site-packages:
#     if uv creates it by itself (a stray `uv sync` or `uv run`), the flag is
#     missing and cv2/picamera2 raise ModuleNotFoundError although the system
#     has them. rm -rf heals any such half-done .venv. ---
rm -rf .venv
uv venv --system-site-packages --python /usr/bin/python3 .venv
uv sync --inexact

# --- 7. Verify every import, then serve on port 5000 (open http://<pi-ip>:5000) ---
.venv/bin/python -c "import cv2, numpy, PIL, picamera2, flask, stackprinter, adafruit_servokit; from ai_edge_litert import interpreter; print('all imports OK')" && ./run-app.sh
```


### Python packages (pyproject.toml):
- Adafruit ServoKit https://pypi.org/project/adafruit-circuitpython-servokit/
- ai-edge-litert, the TFLite interpreter. It replaces `tflite-runtime`, which is abandoned upstream (last release supports Python ≤ 3.11): LiteRT is its continuation with the same `Interpreter` API.
- flask + gunicorn (the web UI) and stackprinter (readable tracebacks)

## Running

- As of today, I'm using mobilenet_v2 heavily quantized, which gave me 30fps, compared to 1.6fps on Yolo7 with ONNX.
- run-app.sh runs gunicorn on port 5000

## TODO

- There's something going on with the rectangles and the detection. I am not sure if it's calculating on the small buffer and going to the big one. 
    - I think it's because the inference buffer and the display buffer have to be multiples of each other, but I'm not sure.
- Fine-tune on birds
- A full pipeline for PyTorch's models to be trained in a supercomputer, and quantized and reduced to run at a decent performance on the Raspberry Pi.
- Fix the autofocus on the Pi5. It's not working, and I'm not sure why.

## Acknowledgments:

- The mjpeg server with gunicorn comes from https://github.com/miguelgrinberg/flask-video-streaming