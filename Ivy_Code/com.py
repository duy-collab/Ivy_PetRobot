import smbus
import struct
import serial
import time
import numpy as np
import random
from multiprocessing import Value

class COM():
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.ESP_address = 0x77
        self.serial = serial.Serial(port = "/dev/ttyS0", baudrate = 115200, timeout = 0.05)
        self.ll, self.rl, self.le, self.re = Value('f', 0.0), Value('f', 0.0), Value('f', 0.0), Value('f', 0.0)
        self.error = False
  
        # self.send_motor_speed(0, 0)
    
    def send_motor_speed(self, w_l = 0, w_r = 0):
        data = struct.pack('ff', w_l, w_r)

        try:
            self.bus.write_i2c_block_data(self.ESP_address, 0, list(data))
        except Exception as e:
            print(e)
            self.error = True

    def set_ear(self, l = 0, r = 0):
        ll = 80 + l
        rr = 90 - r
        data = struct.pack('ff', ll, rr)

        try:
            self.bus.write_i2c_block_data(self.ESP_address, 1, list(data))
        except Exception as e:
            print(e)
            self.error = True

        with self.le.get_lock():
            self.le.value = l
        with self.re.get_lock():
            self.re.value = r
    
    def set_leg(self, l = 0, r = 0):
        ll = 93 - l
        rr = 90 + r
        data = struct.pack('ff', ll, rr)

        try:
            self.bus.write_i2c_block_data(self.ESP_address, 2, list(data))
        except Exception as e:
            print(e)
            self.error = True

        with self.ll.get_lock():
            self.ll.value = l
        with self.rl.get_lock():
            self.rl.value = r

    def set_all(self, e_l = 0, e_r = 0, l_l = 0, l_r = 0):
        self.set_ear(e_l, e_r)
        time.sleep(0.01)
        self.set_leg(l_l, l_r)

    def stop_ear(self):
        data = struct.pack('ff', 0.0, 0.0)

        try:
            self.bus.write_i2c_block_data(self.ESP_address, 3, list(data))
        except Exception as e:
            print(e)
            self.error = True

    def stop_leg(self):
        data = struct.pack('ff', 0.0, 0.0)

        try:
            self.bus.write_i2c_block_data(self.ESP_address, 4, list(data))
        except Exception as e:
            print(e)
            self.error = True

    def stop_all(self):
        self.stop_ear()
        self.stop_leg()
        
    def read_serial(self):
        try:
            data = self.serial.readline().decode("utf-8")
        except Exception as e:
            self.error = True
            data = "Battery:10.0"
        
        return data

def main():
    com = COM()
    com.set_leg()
    time.sleep(2)
    com.stop_ear()

    # for _ in range(50):
    #     com.set_leg(-90, 90)
    #     time.sleep(0.2)
    #     com.set_leg(90, -90)
    #     time.sleep(0.2)

    # com.stop_all()

if __name__ == "__main__":
    main()

        