import io
import time
from picamera2 import Picamera2, Preview, MappedArray
from base_camera import BaseCamera
from servo import *

import logging
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image, ImageDraw, ImageFont


def ReadLabelFile(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret


servo = Servo()
target = "cell phone"
rectangles = []
normalSize = (640, 480)
lowresSize = (320, 240)
labels = ReadLabelFile("coco_labels.txt")


def defineMovement(center):
    # If something is found on the first or last quarter of the image, try to bring it to the center
    if center[0] < (normalSize[0] / 3):
        logging.info("moving left")
        servo.left()
    if center[0] > (normalSize[0] - (normalSize[0] / 3)):
        logging.info("moving right")
        servo.right()
    if center[1] < (normalSize[1] / 3):
        logging.info("moving up")
        servo.up()
    if center[1] > (normalSize[1] - (normalSize[1] / 3)):
        logging.info("moving down")
        servo.down()


class Camera(BaseCamera):
    def DrawRectangles(request):
        global target
        # MappedArray writes directly into the camera buffer, not into a copy
        with MappedArray(request, "main") as m:
            for rect in rectangles:
                # logging.info(rect)
                rect_start = (int(rect[0] * 2) - 5, int(rect[1] * 2) - 5)
                rect_end = (int(rect[2] * 2) + 5, int(rect[3] * 2) + 5)
                logging.info("rect_start:", rect_start, "rect_end:", rect_end)
                cv2.rectangle(m.array, rect_start, rect_end, (0, 255, 0, 0))
                center = (
                    rect_start[0] + int((rect_end[0] - rect_start[0]) / 2),
                    rect_end[1] + int((rect_start[1] - rect_end[1]) / 2),
                )
                cv2.circle(m.array, center, radius=5, color=(255, 0, 0), thickness=20)

                # I only follow one category
                if rect[4] == target:
                    # logging.info("Found ", target)
                    defineMovement(center)

                if len(rect) >= 5:
                    text = rect[4] + ": {:.2f}".format(rect[5] * 100) + "%"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(
                        m.array,
                        text,
                        (int(rect[0] * 2) + 10, int(rect[1] * 2) - 12),
                        font,
                        2,
                        (255, 255, 255),
                        4,
                        cv2.LINE_AA,
                    )

    def InferenceTensorFlow(image, model, output, labels=None):
        global rectangles

        interpreter = tflite.Interpreter(model_path=model, num_threads=4)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        height = input_details[0]["shape"][1]
        width = input_details[0]["shape"][2]
        floating_model = False
        if input_details[0]["dtype"] == np.float32:
            floating_model = True

        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        initial_h, initial_w, channels = rgb.shape

        picture = cv2.resize(rgb, (width, height))

        input_data = np.expand_dims(picture, axis=0)
        if floating_model:
            input_data = (np.float32(input_data) - 127.5) / 127.5

        interpreter.set_tensor(input_details[0]["index"], input_data)

        interpreter.invoke()

        detected_boxes = interpreter.get_tensor(output_details[0]["index"])
        detected_classes = interpreter.get_tensor(output_details[1]["index"])
        detected_scores = interpreter.get_tensor(output_details[2]["index"])
        num_boxes = interpreter.get_tensor(output_details[3]["index"])

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
                    # logging.info(labels[classId], 'score = ', score)
                    rectangles[-1].append(labels[classId])
                    rectangles[-1].append(score)
                else:
                    pass
                    # logging.info('score = ', score)

    @staticmethod
    def frames():
        with Picamera2() as camera:
            config = camera.create_preview_configuration(
                main={"size": normalSize},
                lores={"size": lowresSize, "format": "YUV420"},
            )
            camera.configure(config)

            try:
                camera.set_controls({"AfTrigger": 1})
            except RuntimeError as e:
                logging.error(f"This camera has no autofocus: {e}")
                # handle the error here or re-raise if you cannot handle it
            stride = camera.stream_configuration("lores")["stride"]
            camera.pre_callback = Camera.DrawRectangles

            camera.start()
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            try:
                while True:
                    buffer = camera.capture_buffer("lores")
                    grey = buffer[: stride * lowresSize[1]].reshape(
                        (lowresSize[1], stride)
                    )

                    # The inference sets rectangles, and the callback draws them on the buffer, so I capture the image twice
                    result = Camera.InferenceTensorFlow(
                        grey,
                        "mobilenet_v2.tflite",
                        "",
                        labels,
                    )
                    camera.capture_file(stream, format="jpeg")
                    stream.seek(0)
                    yield stream.read()

                    # reset stream for next frame
                    stream.seek(0)
                    stream.truncate()
            finally:
                camera.stop()
