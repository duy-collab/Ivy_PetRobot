from src.lcd.lcd import LCD
from src.mpu.mpu import MPU
from src.com.com import COM
from src.cam.cam import Cam
from src.rgb.rgb import RGB
from src.mqtt.mqtt_localhost import MQTT
from src.mqtt.mqtt_disconnect import MQTT_DIS
# from src.mqtt.mqtt_hive_sever import MQTT
from src.mic.mic import Mic
from src.fuzzy.fuzzy import Fuzzy
from src.openapi.openapi import Openapi
from src.yolov8.yolov8 import Yolov8

from multiprocessing import Value, Event, Array
from threading import Thread
from queue import Queue
import sys


import RPi.GPIO as GPIO

import ast

import time
from datetime import datetime, timedelta 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# mpu = MPU()
com = COM()
cam = Cam()
fuz = Fuzzy()
lcd = LCD()
rgb = RGB()

try:
    mqtt = MQTT()
except Exception as e:
    mqtt = MQTT_DIS()

opi = Openapi()
mic = Mic()
yl8 = Yolov8()

express = Value('i', 0)
state   = Value('i', 0)
error   = Value('f', 0.0)
width   = Value('f', 0.0)
battery = Value('i', 100)

# Sensors
# ax, ay, az, aN, aE, aD, roll, pitch, yaw = [Value('f', 1.0) for _ in range(9)]

# Friendly
contents = 70.0
try:
    with open('/home/pi/Ivy/src/friendly.txt', 'r') as file:
        contents = file.read()
        contents = float(contents)
except Exception as e:
    contents = 70.0

friendly = Value('f', contents)

# Robots
radius  = 0.085                             # m 
length  = 0.17                              # m 
w_m_max = 13.0                              # rad / s
v_max   = radius * w_m_max                  #  m / s
w_max   = 2 * radius * w_m_max / length     # rad / s

# Running
running = Event()
running.set()

acting = Event()
acting.clear()

look_around = Event()
look_around.clear()

# Battery
low_battery_count = Value('i', 0)

# Internet
internet = Event()
internet.clear()

# Error
err = Event()
err.clear()

# Microphone
voice = Array('B', 10 * 1024 * 1024) # 10 MB buffer
voice_len = Value('i', 0)
halucination = ["Thank you.", "You're going to.", "We're here.", "Thanks for watching!", " ", "You", "Thank you for watching!", "you", ""] 

chatting = Event()
chatting.clear()

express_dictionary = ["idle",               # 0
                      "angry",              # 1
                      "glare",              # 2
                      "happy",              # 3
                      "love",               # 4
                      "sad",                # 5
                      "sleep",              # 6
                      "wrinkle",            # 7
                      "idle_bello",         # 8
                      "idle_birthday",      # 9
                      "idle_cat",           # 10
                      "idle_cow",           # 11
                      "idle_dizzy",         # 12
                      "idle_dog",           # 13
                      "idle_duck",          # 14
                      "idle_elephant",      # 15
                      "idle_hi",            # 16
                      "idle_what",          # 17
                      "idle_optimus",       # 18
                      "idle_unknown",       # 19
                      "idle_what2",         # 20
                      "idle_optimus2",      # 21
                      "idle_angry2",        # 22
                      "idle_angry3",        # 23
                      "idle_angry4",        # 24
                      "idle_bye",           # 25
                      "idle_love",          # 26
                      "idle_mumble",        # 27
                      "idle_let_me_see",    # 28
                      "idle1",              # 29
                      "idle2",              # 30
                      "idle3",              # 31
                      "idle4",              # 32
                      "idle5",              # 33
                      "idle6",              # 34
                      "idle7",              # 35
                      "idle8",              # 36
                      "idle9",              # 37
                      "idle10",             # 38
                      "idle11",             # 39
                      "idle_battery",       # 40
                      "talking",            # 41
                      "listen1",            # 42
                      "listen2",            # 43
                      "wrinkle2",           # 44
                      "thinking",           # 45
                      "paint",              # 46
                      "idle_hate",          # 47
                      "idle_sigh",          # 48
                      "idle_connection",    # 49
                      "show",               # 50
                      "lookleft",           # 51
                      "lookright",          # 52
                      "lookcenter",         # 53
                      "error",              # 54
                      ]        

state_dictionary = ["stand still",          # 0
                    "follow",               # 1
                    "go around",            # 2
                    ]

animal_dictionary = {"cat": 10,
                     "dog": 13,
                     "cow": 11,
                     "elephant": 15,
                     "duck": 14}