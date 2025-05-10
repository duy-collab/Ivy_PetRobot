from src.utility.utils import *

from multiprocessing import Process
        
def lcd_process():
    while running.is_set():
        try:
            if lcd.current_express == "idle_optimus" or lcd.current_express == "idle_optimus2":
                if lcd.current_index == 1:
                    lcd.fps = 10
                elif lcd.current_index == len(lcd.package[lcd.current_express]) - 1:
                    lcd.fps = 16

            expression = express_dictionary[express.value]
            lcd.show_expression(expression)

            if "idle_" in expression and lcd.current_index == len(lcd.package[lcd.current_express]) - 1:
                with express.get_lock():
                    express.value = 0

            if lcd.current_express == "idle5" and lcd.current_index == 0:
                look_around.set()
                time.sleep(0.2)

            if express.value == 25 and lcd.current_index == len(lcd.package[lcd.current_express]) - 1:
                lcd.switch(on = False)

            if lcd.current_express == "paint_to_idle" and lcd.current_index == 14:
                time.sleep(10)

        except KeyboardInterrupt:
            break

        except Exception as e:
            err.set()
            print(e)
        
def battery_process():
    while running.is_set():
        try:
            data = com.read_serial()
            if data != "":
                if "Battery" in data:
                    voltage = data.split(":")[-1]
                    voltage = float(voltage)
                    battery_percent = - 27.318 * voltage * voltage + 703.36 * voltage - 4428.1
                    with battery.get_lock():
                        battery.value = max(5, min(100, int(battery_percent)))

                    if battery.value <= 20:
                        with low_battery_count.get_lock():
                            low_battery_count.value = low_battery_count.value + 1
                    else:
                        with low_battery_count.get_lock():
                            low_battery_count.value = 0
        except KeyboardInterrupt:
            break

        except Exception as e:
            err.set()
            print(e)

def upload_image_process():
    while running.is_set():
        try:
            if state_dictionary[state.value] == "go around" or state_dictionary[state.value] == "follow": 
                frame = cam.get_image()
                encoded_image = cam.encode_image(frame, quality = 40)
                mqtt.upload_image(encoded_image)

        except KeyboardInterrupt:
            break
        
        except Exception as e:
            err.set()
            print(e)

def stop_holding_process():
    this_timer = time.perf_counter()
    stop_holding = True
    while running.is_set():
        try:
            if not acting.is_set():
                if stop_holding:
                    if time.perf_counter() - this_timer >= 0.25:
                        if com.ll.value == 0 and com.rl.value == 0 and com.le.value  == 0 and com.re.value == 0:
                            com.stop_all()
                            stop_holding = False
                        this_timer = time.perf_counter()
                else:
                    if time.perf_counter() - this_timer >= 3.0:
                        if com.ll.value == 0 and com.rl.value == 0 and com.le.value == 0 and com.re.value  == 0:
                            com.set_ear(0, 0)
                            com.set_leg(0, 0)
                            stop_holding = True
                        this_timer = time.perf_counter()
            else:
                stop_holding = True
                this_timer = time.perf_counter()

        except KeyboardInterrupt:
            break

        except Exception as e:
            err.set()
            print(e)

def main():
    acting.set()

    # Create a process for battery calculation
    battery_instance = Process(target = battery_process)
    battery_instance.start()

    # Create a process for image capturing
    upload_image_instance = Thread(target = upload_image_process)
    upload_image_instance.start()

    # Create a process for the lcd display
    lcd_instance = Process(target = lcd_process)

    touch_setup()
    vc_setup()

    com.send_motor_speed(0, 0)
    com.set_ear(0, 0)
    com.set_leg(0, 0)

    # Mumble timing
    sound_timing = time.perf_counter()
    sound_waiting = random.randint(180, 240)

    do_hi = False
    do_sigh = False

    friendly_value = friendly.value
    if friendly_value < 30:
        do_sigh = True
    elif friendly_value < 50:
        do_sigh = random.choices([True, False], [0.3, 0.7])[0]
    else:
        do_sigh = False
    
    if do_sigh:
        sigh()
        lcd_instance.start()
        for i in range(100, -1, -1):
            rgb.light = i
            rgb.set_battery()
            time.sleep(0.04)
        
    else:
        do_hi = random.choices([True, False], [0.8, 0.2])[0]
        hi()
        lcd_instance.start()
    
    rgb.light = 100
    rgb.set_battery()

    if do_hi:
        which_leg = random.choice([1, -1])
        range_leg(0, 15 * which_leg, 0 , -15 * which_leg, 100, 0.6)
        time.sleep(2)
        range_leg(15 * which_leg, 0 , -15 * which_leg, 0, 100, 0.6)

    acting.clear()

    # Stop holding process
    stop_holding_instance = Process(target = stop_holding_process)
    stop_holding_instance.start()

    try:  
        while running.is_set():
            try:
                if look_around.is_set():
                    acting.set()
                    play_sound("/home/pi/Ivy/src/speaker/audio_package/look_around.wav", wait = True)
                    look_around.clear()
                    acting.clear()

                if low_battery_count.value >= 8:
                    if not acting.is_set():
                        low_battery()

                        with low_battery_count.get_lock():
                            low_battery_count.value = 0
                    else:
                        with low_battery_count.get_lock():
                            low_battery_count.value = 4

                if battery.value != rgb.light:
                    rgb.light = battery.value 
                    if not acting.is_set():
                        rgb.set_battery()

                if state_dictionary[state.value] == "stand still":
                    # Mumble
                    if time.perf_counter() - sound_timing >= sound_waiting:
                        if not acting.is_set():
                            acting.set()
                            sound_timing = time.perf_counter()
                            sound_waiting = random.randint(180, 240)

                            friendly_value = friendly.value
                            if friendly_value < 30:
                                sigh()
                            else:
                                mumble()
                            acting.clear()
                        else:
                            sound_timing = time.perf_counter()

                elif state_dictionary[state.value] == "follow":                      
                    ee, rr = mqtt.track
                    if ee == -999 or rr == -999:
                        with express.get_lock():
                            express.value = 53
                    else:
                        follow_process(ee, rr)
                elif state_dictionary[state.value] == "go around":
                    ll, ff, rr = mqtt.depth
                    if ll == -1.0 or ff == -1.0 or rr == -1.0:
                        continue
                    else:
                        go_around_process(ll, ff, rr)

                if com.error:
                    pass
                    # err.set()

                if err.is_set():
                    got_error()

            except KeyboardInterrupt:
                break

    except Exception as e:
        print(e)
        err.set()
        got_error()
        
    finally:
        com.send_motor_speed(0, 0)
        # com.stop_ear()
        # com.stop_leg()

        save_friendly()
        running.clear()
        
        lcd_instance.join()
        battery_instance.join()
        upload_image_instance.join()
        stop_holding_instance.join()
        # mpu_instance.join()
        
        lcd.switch(on = False)
        rgb.stop()
        cam.stop_camera()
        mqtt.disconnect()
        GPIO.cleanup()

        # sys.exit(0)
        
if __name__ == "__main__":
    main()
