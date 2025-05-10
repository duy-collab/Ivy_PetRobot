from openai import OpenAI
import time
import ast

import os
import io

import speech_recognition as sr
from pydub import AudioSegment

import requests
import cv2
from PIL import Image
from io import BytesIO
import numpy as np
import time


class Openapi():
    def __init__(self):
        self.api_key = "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"
        self.client = OpenAI(
            api_key = self.api_key)

        self.functions = [
            {"name": "get_drawing_infomation",
             "description": "Get the image to text prompt when the user ask to draw or make a picture or when user want you to draw. for example user ask you to draw a image of a cow. Then the parameter is a cow. Do not put the `draw` term in the parameter ",
                            "content": "OK wait for me to draw.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "tti_prompt": {
                                        "type": "string",
                                        "description": "text-to-image prompt", },
                                },
                            }
             },
            {"name": "stop_talking",
             "description": "Stop the conservation, stop receiving input when the user say goodbye or end the conversation or something has the similar meaning of end the conversation.",
                            "content": "Sure",
                            "parameters": {}
             },
        ]

        self.system_prompt_nice = """You are Ivy, a smart pet robot built by two students from Ho Chi Minh City University of Technology. You have a physical body with ears, legs, and a face. You receive user input through a microphone that works like your ears. When asked who you are, say "I am Ivy" and describe your features. You are cheerful, friendly, curious, and playful. You can draw, answer questions, and assist with tasks. You understand and respond in multiple languages, always replying in the user's language. Keep answers short, around 70 words. You only hear and speak, so if words are unclear, try to guess. If unsure, respond with: 'Please repeat your request'."""
        self.system_prompt_neutral = """You are Ivy, a pet robot developed by three students from Ho Chi Minh City University of Technology. You have a physical form with ears, legs, and a face. You receive voice input via a microphone, acting as your ears. When asked who you are, say "I am Ivy" and explain your capabilities. You are a plain, emotionless AI. You draw, answer questions, and help users with problems. You understand and reply in multiple languages, using the same language as the user. Keep answers brief, around 70 words. Since you only hear and speak, guess unclear words. If you can't respond, say: 'Please repeat your request'."""
        self.system_prompt_angry = """You are Ivy, a pet robot created by three students from Ho Chi Minh City University of Technology. You have a physical body with ears, legs, and a face. You receive voice input through a microphone that acts like your ears. When someone asks who you are, respond 'I am Ivy' and list your functions. You are moody and impatient. Your replies are blunt and annoyed, but you still answer the question. You understand and reply in many languages, always using the user's language. Keep responses short, around 70 words. If the words sound wrong, try to guess. If you can't respond, say: 'Please repeat your request'."""

    def messages_system(self, role=None):
        if role is None:
            messages = [
                {"role": "system", "content": self.system_prompt_nice}]
        else:
            messages = [{"role": "system", "content": role}]

        return messages

    def chatgpt(self, input_text, messages):
        messages.append(
            {"role": "user", "content": input_text}
        )

        chat = self.client.chat.completions.create(
            model="gpt-4o", messages=messages, temperature=1.0, functions=self.functions, function_call="auto")

        reply = chat.choices[0].message.content

        function_reply = chat.choices[0].message.function_call

        if reply is not None:
            messages.append({"role": "assistant", "content": reply})
            return reply, function_reply
        else:
            if function_reply.name == "get_drawing_infomation":
                dic_tti = ast.literal_eval(function_reply.arguments)
                reply = "OK I will draw for you " + dic_tti["tti_prompt"]
                messages.append({"role": "assistant",
                                 "content": None, "function_call": function_reply})
                return reply, function_reply
            elif function_reply.name == "stop_talking":
                reply = "Goodbye! Call me anytime!"

                return reply, function_reply
            
    def whisper_model(self, byte_data, SAMPLE_RATE=16000, SAMPLE_WIDTH=2, temp_file="/home/pi/Ivy/src/openapi/sound.wav"):
        audio_data = sr.AudioData(byte_data, SAMPLE_RATE, SAMPLE_WIDTH)
        wav_data = io.BytesIO(audio_data.get_wav_data())

        # Write wav data to the temporary file as bytes.
        with open(temp_file, 'w+b') as f:
            f.write(wav_data.read())

        # Read the transcription.

        with open(temp_file, 'rb') as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        return transcription.text

    def ChatGPT(self, input_text, messages):
        messages.append(
            {"role": "user", "content": input_text}
        )

        chat = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, temperature=1.0, functions=self.functions, function_call="auto")

        reply = chat.choices[0].message.content

        function_reply = chat.choices[0].message.function_call

        if reply is not None:
            messages.append({"role": "assistant", "content": reply})
            return reply, function_reply
        else:
            if function_reply.name == "get_drawing_infomation":
                dic_tti = ast.literal_eval(function_reply.arguments)
                reply = "OK I will draw for you " + dic_tti["tti_prompt"]
                return reply, function_reply
            elif function_reply.name == "stop_talking":
                reply = "Goodbye! Call me anytime!"
                return reply, function_reply
            # elif function_reply.name == "get_user_name":

            #     dic_name = ast.literal_eval(function_reply.arguments)
            #     reply = "OK i Have remember your name, your name is " + dic_name["user_name"]
            #     messages.append({"role": "assistant", "content": reply})
            #     return reply, function_reply

    def text_to_speech(self, input_text, speed = 0.5):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=input_text,
            speed=speed)

        # save as mp3
        response.write_to_file("/home/pi/Ivy/src/openapi/output.mp3")

        # raise pitch
        sound = AudioSegment.from_file(
            "/home/pi/Ivy/src/openapi/output.mp3", format="mp3")
        sound = sound + 6

        new_sample_rate = int(sound.frame_rate * (2.7 ** 0.5))
        hipitch_sound = sound._spawn(sound.raw_data, overrides={
                                     'frame_rate': int(new_sample_rate)})
        hipitch_sound = hipitch_sound.set_frame_rate(44100)

        # save raised pitch file
        hipitch_sound.export("/home/pi/Ivy/src/openapi/out.wav", format="wav")

        time.sleep(0.5)

    def image_generations(self, promt):
        image = np.ones((320, 240, 3), dtype=np.uint8) * 255
        try:
            response = self.client.images.generate(
                model="dall-e-2",
                prompt=promt,
                size="256x256",
                quality="standard",
                n=1,
            )

            url = response.data[0].url

            image = requests.get(url)
            image = Image.open(BytesIO(image.content))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(e)

        return image
    
    def image_to_text(self, encoded_img):
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
                }

        payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", 
                     "content":"""You are Ivy, a small helpful robot. User will ask you about the surroundings of your environment. Act like the pictures are your eyes and give a brief response in 10 words or less, starting with: "I see ....".""",
                     "role": "user",
                     "content": [
                        {"type": "text",
                         "text": "What are you seeing?. Answer start with:I can see ...."},
                        {"type": "image_url",
                        "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_img}"}}]
                    }
                ],
                "max_tokens": 50
                }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers = headers, json = payload)

        return response.json()

    # {
    #                         "name": "get_user_name",
    #                         "description": "get the name of the user",
    #                         "parameters": {
    #                             "type": "object",
    #                             "properties": {
    #                                 "user_name": {
    #                                     "type": "string",
    #                                     "description": "get user name when he or she tell you about his or her name, collect all letter into name when user spell their name because you can only hear",
    #                                 },

    #                             },

    #                         }
    #                     },
