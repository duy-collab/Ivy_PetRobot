import RPi.GPIO as GPIO
import time
import random
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class RGB():
    def __init__(self):
        self.light = 100
        self.setup()
        
    def setup(self):
        for pin in [16, 12, 8,  22, 27, 4]:
                                                #rgb1[blue green red] = [16 12 8]
                                                #rgb2[blue green red] = [22 27 4]
            GPIO.setup(pin, GPIO.OUT, initial = 0)

        self.rl = GPIO.PWM(8, 100)
        self.gl = GPIO.PWM(12, 100)
        self.bl = GPIO.PWM(16, 100)

        self.rr = GPIO.PWM(4, 100)
        self.gr = GPIO.PWM(27, 100)
        self.br = GPIO.PWM(22, 100)

        for led in [self.rl, self.gl, self.bl, self.rr, self.gr, self. br]:
            led.start(0)

    def set_dc_right(self, r, g, b):
        self.rr.ChangeDutyCycle(r)
        self.gr.ChangeDutyCycle(g)
        self.br.ChangeDutyCycle(b)
    
    def set_dc_left(self, r, g, b):
        self.rl.ChangeDutyCycle(r)
        self.gl.ChangeDutyCycle(g)
        self.bl.ChangeDutyCycle(b)
    
    def set_dc(self, r, g, b):
        self.set_dc_left(r, g, b)
        self.set_dc_right(r, g, b)

    def set_rate_right(self, r, g, b):
        self.set_dc_right(int(r * self.light), int(g * self.light), int(b * self.light))

    def set_rate_left(self, r, g, b):
        self.set_dc_left(int(r * self.light), int(g * self.light), int(b * self.light))

    def set_rate(self, r, g, b):
        self.set_rate_right(r, g, b)
        self.set_rate_left(r, g, b)

    def set_val_right(self, r, g, b):
        self.set_rate_right(r / 255, g / 255, b / 255)

    def set_val_left(self, r, g, b):
        self.set_rate_left(r / 255, g / 255, b / 255)
    
    def set_val(self, r, g, b):
        self.set_val_right(r, g, b)
        self.set_val_left(r, g, b)

    def set_battery(self):
        self.set_rate_right(0, 0.3, 0.9)
        self.set_rate_left(0, 0.3, 0.9)

    def stop(self):
        for led in [self.rl, self.gl, self.bl, self.rr, self.gr, self. br]:
            led.stop()

if __name__ == "__main__":
    rgb = RGB()
    
    rgb.set_battery()
    # time.sleep(1)
    while True:
        # continue
        for (r,g,b) in [[100, 0, 0], [0, 100, 0], [0, 0, 100]]:
            rgb.set_dc_right(r, g, b)
            rgb.set_dc_left(r, g, b)
            time.sleep(1)


