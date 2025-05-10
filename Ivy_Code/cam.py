import cv2
import base64
import time
from picamera2 import Picamera2
import time
import numpy as np

class Cam():
    def __init__(self):
        self.img = np.zeros((320, 320, 3), dtype = np.uint8)
        self.set_camera()

    def set_camera(self):
        self.camera = Picamera2()
        camera_config = self.camera.create_video_configuration({"size": (640, 640)})
        self.camera.configure(camera_config)
        self.camera.start()

    def get_image(self, im_size = 320):
        img = self.camera.capture_array()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (im_size, im_size))

        img = cv2.rotate(img, cv2.ROTATE_180)
        
        return img

    def encode_image(self, img, quality = 20):
        _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        encoded = base64.b64encode(buffer)
        return encoded

    def stop_camera(self):
        self.camera.stop()

if __name__ == "__main__":
    cam = Cam()

    while True:
        img = cam.get_image()
        cv2.imwrite("src/cam/cam.jpg", img)