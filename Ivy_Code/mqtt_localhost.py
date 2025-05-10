import paho.mqtt.client as mqtt
import time
import json

from multiprocessing import Process, Event


class MQTT():
    def __init__(self):
        self.connected = True
        # self.broker = "aTinozg.local"
        self.broker = "192.168.10.239"
        self.camera_topic  = "ivy/cam"
        self.empty_topic   = "ivy/empty"
        self.depth_topic   = "ivy/depth"
        self.track_topic   = "ivy/track"
        self.state_topic   = "ivy/state"
        self.detect_topic  = "ivy/detect"
        self.check_topic   = "ivy/check"

        self.client_publish = mqtt.Client()
        self.client_publish.on_connect = self.on_connect_publish
        self.client_publish.connect(self.broker, 1883)
        self.client_publish.loop_start()

        self.maintain_running = Event(); self.maintain_running.set()
        self.maintain_process = Process(target = self.maintain)
        self.maintain_process.start()

        self.client_depth = mqtt.Client()
        self.client_depth.on_connect = self.on_connect_depth
        self.client_depth.on_message = self.on_message_depth
        self.client_depth.connect(self.broker, 1883)
        self.client_depth.loop_start()

        self.client_track = mqtt.Client()
        self.client_track.on_connect = self.on_connect_track
        self.client_track.on_message = self.on_message_track
        self.client_track.connect(self.broker, 1883)
        self.client_track.loop_start()

        self.client_detect = mqtt.Client()
        self.client_detect.on_connect = self.on_connect_detect
        self.client_detect.on_message = self.on_message_detect
        self.client_detect.connect(self.broker, 1883)
        self.client_detect.loop_start()

        self.client_status = mqtt.Client()
        self.client_status.on_connect = self.on_connect_status
        self.client_status.on_message = self.on_message_status
        self.client_status.connect(self.broker, 1883)
        self.client_status.loop_start()

        self.depth = [-1.0, -1.0, -1.0]

        self.track = [-999, -999]

        self.detect = {}

        self.status = ""

    def on_connect_depth(self, client, userdata, flags, rc):
        print(f"Connected to depth topic with result code {rc}")
        self.client_depth.subscribe(self.depth_topic, qos = 0)

    def on_message_depth(self, client, userdata, msg):
        data = msg.payload
        data = data.decode('utf-8')
        data = data.split(",")
        self.depth = [round(float(data[0]) / 255.0, 2), round(float(data[1]) / 255.0, 2), round(float(data[2]) / 255.0, 2)]

    def on_connect_track(self, client, userdata, flags, rc):
        print(f"Connected to track topic with result code {rc}")
        self.client_track.subscribe(self.track_topic, qos = 0)

    def on_connect_status(self, client, userdata, flags, rc):
        print(f"Connected to status topic with result code {rc}")
        self.client_status.subscribe(self.check_topic, qos = 0)

    def on_message_status(self, client, userdata, msg):
        data = msg.payload
        self.status = data.decode()

    def on_message_track(self, client, userdata, msg):
        data = msg.payload
        data = data.decode('utf-8')
        data = data.split(",")
        self.track = [float(data[0]), float(data[1])]

    def on_connect_detect(self, client, userdata, flags, rc):
        print(f"Connected to detect topic with result code {rc}")
        self.client_detect.subscribe(self.detect_topic, qos = 0)

    def on_message_detect(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        self.detect = json.loads(payload)

    def on_connect_publish(self, client_publish, userdata, flags, rc):
        print(f"Connected to publish node with result code {rc}")

    def upload_image(self, encoded_image):
        self.client_publish.publish(self.camera_topic, encoded_image, retain = False, qos = 0)

    def upload_state(self, data):
        self.client_publish.publish(self.state_topic, data, retain = False, qos = 0)

    def maintain(self):
        while self.maintain_running.is_set():
            try:
                self.client_publish.publish(self.empty_topic, "", retain = False, qos = 0)
                time.sleep(30)
            except KeyboardInterrupt:
                break
        print("Stop")

    def disconnect(self):
        self.maintain_running.clear()
        self.maintain_process.join()
        self.client_publish.loop_stop()
        self.client_publish.disconnect()
        print("Disconnected successfully!")
