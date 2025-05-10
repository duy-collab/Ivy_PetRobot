# Ivy_PetRobot

Ivy_PetRobot is an interactive AI-powered pet robot designed to engage with users through voice, facial recognition, and dynamic behaviors. It brings personality to robotics with a focus on emotional expression and smart interaction.

## Features

- 🎤 Voice recognition using Whisper
- 🗣️ Speech synthesis with natural voice
- 🧠 AI-powered conversation using OpenAI API
- 📷 Image recognition and scene description
- 😺 Facial emotion display via LCD and LED
- 🛞 Motor control for mobility and animation
- 🕹️ ESP32 & Raspberry Pi integration
- 📡 MQTT cloud communication with HiveMQ
- 📁 I2C communication for command synchronization

## Technologies Used

- Raspberry Pi OS Bullseye
- ESP32 microcontroller
- INMP441 microphone (I2S)
- MAX98357A speaker amp (I2S)
- ILI9341 / ST7796 LCD with GT911 touch
- OpenAI Whisper and GPT APIs
- HiveMQ MQTT for IoT data streaming
- Python, C++ (Arduino), Bash

## Repository Structure

/Ivy_PetRobot
├── raspberry_pi/ # Main AI logic, image processing, audio I/O

├── esp32/ # Display, motors, expression handling

├── arduino_nano/ # Optional: audio capture and I2C transmission

├── assets/ # Face expression images, sound files

├── docs/ # Reports and design documentation

└── README.md

## Credits

Final year thesis project by Luong Ho Khanh Duy, Student ID 2113013 and Tran Kim Khanh, Student ID 2113717 — Department of Electrical Engineering, Ho Chi Minh City University of Technology (HCMUT).
