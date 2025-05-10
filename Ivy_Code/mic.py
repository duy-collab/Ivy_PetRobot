import time
import io
import speech_recognition as sr
import numpy as np
import sounddevice 

from datetime import datetime, timedelta 
from queue import Queue


class Mic():
    def __init__(self):
        self.set_recognizer()
        self.set_microphone()
        print("Ready to recognize!!")

    def set_recognizer(self, energy_threshold = 1750):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True

    def set_microphone(self, microphone_name = "default"):
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            if name == microphone_name:
                self.microphone = sr.Microphone(device_index = i, sample_rate = 16000)
                break

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def amplify_audio(self, data, amplification_factor = 3.0):
        audio_data = np.frombuffer(data, np.int16)
        audio_data = np.clip(audio_data * amplification_factor, -32768, 32767)
        amplified_data = audio_data.astype(np.int16).tobytes()

        return amplified_data

    def listen(self):
        phrase_timeout = 1
        phrase_time = None
        
        queue = Queue()
        last_sample = bytes()
        amplified_data = bytes()

        while True:
            with self.microphone as source:
                audio = self.recognizer.listen(source) 

            print("Listening")
        
            now = datetime.utcnow()
            data = audio.get_raw_data()
        
            queue.put(data)
            
            if not queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds = phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True

                phrase_time = now

                while not queue.empty():
                    data = queue.get()
                    last_sample += data

                if phrase_complete:
                    print("Boom!")
                    amplified_data = self.amplify_audio(last_sample)
                    
                    return amplified_data
                    
            else:
                # Infinite loops are bad for processors, must sleep.
                time.sleep(0.25)
        
        

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    test = Mic()
    test.set_recognizer()
    test.set_microphone()
    data = test.listen()
    audio_data = sr.AudioData(data, 16000, 2)
    wav_data = io.BytesIO(audio_data.get_wav_data())

    with open("sound.wav", 'w+b') as f:
        f.write(wav_data.read())