import digitalio
import board
from PIL import Image, ImageDraw
from adafruit_rgb_display import ili9341

import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import time
import random

class LCD():  
    def __init__(self):
        self.CS = digitalio.DigitalInOut(board.CE1)
        self.DC = digitalio.DigitalInOut(board.D17)
        self.RES = digitalio.DigitalInOut(board.D23)
        self.LED = digitalio.DigitalInOut(board.D24)
        self.LED.direction = digitalio.Direction.OUTPUT
        
        self.BAUDRATE = 60000000

        self.SPI = board.SPI()
        self.screen = ili9341.ILI9341(self.SPI, rotation = 270, cs = self.CS, dc = self.DC, rst = self.RES, baudrate = self.BAUDRATE)
        self.width, self.height = self.get_size()

        self.draw_blank()
        self.current_index = 0
        self.current_express = "idle_bello" if random.randint(0, 1) == 0 else "idle_hi"

        self.expression_path = "/home/pi/Ivy/src/lcd/face_expression"
        self.load_package()
        self.switch(on = True)

        self.fps = 16

    def load_package(self):
        self.package = {}
        for expression_pack in os.listdir(self.expression_path):
            for expression in os.listdir(f"{self.expression_path}/{expression_pack}"):
                self.package[expression] = []
                n_images = len(os.listdir(f"{self.expression_path}/{expression_pack}/{expression}"))
                for i in range(n_images):
                    self.package[expression].append(f"{self.expression_path}/{expression_pack}/{expression}/{i}.jpg")

    def get_size(self):
        if self.screen.rotation % 180 == 90:
            height = self.screen.width 
            width = self.screen.height
        else:
            width = self.screen.width 
            height = self.screen.height
        return width, height

    def load_image(self, path):
        image = Image.open(path)
        # image = self.resize_image(image)
        return image

    def resize_image(self, image):
        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = self.width / self.height

        if screen_ratio < image_ratio:
            scaled_width = image.width * self.height // image.height
            scaled_height = self.height
        else:
            scaled_width = self.width
            scaled_height = image.height * self.width // image.width

        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - self.width // 2
        y = scaled_height // 2 - self.height // 2

        image = image.crop((x, y, x + self.width, y + self.height))

        return image

    def show_expression(self, express):
        if express not in self.current_express:
            if "idle" not in express:
                self.current_express = "idle" + "_to_" + express
                self.current_index = 0
            else:
                if "idle" not in self.current_express:
                    self.current_express = self.current_express + "_to_" + "idle"
                    self.current_index = 0
                else:
                    self.current_express = express
                    self.current_index = 0
        self.draw_expression()

    def switch(self, on = True):
        self.LED.value = on
            
    def draw_image(self, image):
        self.screen.image(image)
        time.sleep(0.01)

    def draw_blank(self):
        image = Image.new("RGB", (self.width, self.height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))

        self.draw_image(image)

    def draw_expression(self):
        start_drawing = time.perf_counter()
        image = self.load_image(self.package[self.current_express][self.current_index])
        self.draw_image(image)
        
        self.current_index += 1

        if self.current_index >= len(self.package[self.current_express]):
            if "to" in self.current_express:
                self.current_express = self.current_express.split("_")[-1]
            if "idle" in self.current_express:
                idle_express = self.current_express
                while idle_express == self.current_express:
                    idle_express = random.choices(["idle1", "idle2", "idle3", "idle4", "idle5", "idle6", "idle7", "idle8", "idle9", "idle10", "idle11"], 
                                                  [    0.8,    0.02,    0.02,    0.02,    0.02,    0.02,    0.02,    0.02,    0.02,     0.02,     0.02])[0]
                    if idle_express == "idle1":
                        break
                
                self.current_express = idle_express
            self.current_index = 0
        
        stop_drawing = time.perf_counter() - start_drawing
        if stop_drawing < 1 / self.fps:
            time.sleep(1 / self.fps - stop_drawing)


if __name__ == "__main__":
    lcd = LCD()
    timing = time.perf_counter()
    express = lcd.current_express
    exps = list(lcd.package.keys())
    exps = [element for element in exps if 'to' not in element]
    i = 0
    time.sleep(1)         
    
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
                      ]        

    # exp = express_dictionary[25]
    # exp = express_dictionary[40]
    lcd = LCD()
    time.sleep(1)    
    i = 0
    anm = ["birthday", "cow", "dog", "duck", "elephant"]
    exp = "idle_" + anm[i]
    while True:
        st = time.perf_counter()
        lcd.show_expression(exp)
        print(1 / (time.perf_counter() - st))
        if lcd.current_express == exp and lcd.current_index == len(lcd.package[lcd.current_express]) - 1:
            i = (i + 1) % 5
            exp = "idle_" + anm[i]
