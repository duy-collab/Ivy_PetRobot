#include <Arduino.h>
#include <Wire.h>

// I2C Address
#define ESP32_ADDRESS 0x77

// Motor control pins
#define IN1 33
#define IN2 25
#define IN3 26
#define IN4 27
#define ENA 32
#define ENB 14

// Encoder pins
#define C1A 23
#define C1B 13
#define C2A 5
#define C2B 15

// Servo PWM pins
#define E1 2
#define E2 4
#define A1 18
#define A2 19

// Servo configuration
const int servo_freq = 50;
const int servo_resolution = 12;
const int servo_channels[4] = {0, 1, 2, 3};
int servo_limits[2] = {0, 0};

// Motor parameters
const int DC_freq = 5000;
const int DC_resolution = 8;
const int DC_channels[2] = {4, 5};
const float ENC_COUNTS_PER_REV = 330.0;
const int SAMPLE_TIME_MS = 50;

// PID parameters
const float Kp[2] = {18.12, 18.44};
const float Ki[2] = {382.9, 382.15};

// Global variables
volatile int encoder_ticks[2] = {0, 0};
float target_speeds[2] = {0};
float current_speeds[2] = {0};
float integral_errors[2] = {0};
int motor_outputs[2] = {0};

// Servo angles
float servo_angles[4] = {90, 90, 130, 70}; // E1, E2, A1, A2

// Low-pass filter
class LowPassFilter {
  float alpha;
  float filtered;
public:
  LowPassFilter(float cutoff, float sampleRate) {
    float dt = 1.0 / sampleRate;
    float RC = 1.0 / (2 * 3.1416 * cutoff);
    alpha = dt / (RC + dt);
    filtered = 0;
  }

  float update(float input) {
    filtered += alpha * (input - filtered);
    return filtered;
  }
};

LowPassFilter speed_filters[2] = { LowPassFilter(10, 20), LowPassFilter(10, 20) };


// I2C data union
union {
  uint8_t bytes[8];
  float values[2];
} i2c_data;

// Encoder ISR
void IRAM_ATTR encoder1ISR() {
  bool dir = GPIO.in & (1 << C1B);
  encoder_ticks[0] += dir ? 1 : -1;
}

void IRAM_ATTR encoder2ISR() {
  bool dir = GPIO.in & (1 << C2B);
  encoder_ticks[1] += dir ? 1 : -1;
}

// Servo functions
void setupServos() {
  for(int i=0; i<4; i++) {
    ledcSetup(servo_channels[i], servo_freq, servo_resolution);
    ledcAttachPin((const int[]){E1, E2, A1, A2}[i], servo_channels[i]);
  }
  servo_set_range(500, 2400);
}

void servo_set_range(int low_us, int high_us) {
  servo_limits[0] = (low_us * (1 << servo_resolution)) / 20000;
  servo_limits[1] = (high_us * (1 << servo_resolution)) / 20000;
}

void writeServoAngle(int channel, float angle) {
  angle = constrain(angle, 0, 180);
  int duty = map(angle, 0, 180, servo_limits[0], servo_limits[1]);
  ledcWrite(servo_channels[channel], duty);
}

// Motor control
void setMotorDirection(int motor, int dir) {
  const int pins[2][2] = {{IN1, IN2}, {IN3, IN4}};
  digitalWrite(pins[motor][0], dir == 1);
  digitalWrite(pins[motor][1], dir == -1);
}

void updateMotorOutput(int motor) {
  motor_outputs[motor] = constrain(motor_outputs[motor], -255, 255);
  ledcWrite(DC_channels[motor], abs(motor_outputs[motor]));
  setMotorDirection(motor, motor_outputs[motor] > 0 ? 1 : (motor_outputs[motor] < 0 ? -1 : 0));
}

// PID calculation
void updatePID(int motor) {
  if(target_speeds[motor] == 0) {
    integral_errors[motor] = 0;
motor_outputs[motor] = 0;
    return;
  }

  float error = target_speeds[motor] - current_speeds[motor];
  integral_errors[motor] = constrain(integral_errors[motor] + error * SAMPLE_TIME_MS / 1000.0, -5, 3);
  
  float output = Kp[motor] * error + Ki[motor] * integral_errors[motor];
  motor_outputs[motor] = constrain(output, -255, 255);
}

// I2C handler
void receiveEvent(int byteCount) {
  if(byteCount >= 9) {
    uint8_t cmd = Wire.read();
    if(cmd < 3) {
      for(int i=0; i<8; i++) i2c_data.bytes[i] = Wire.read();
      
      if(cmd == 0) {
        target_speeds[0] = i2c_data.values[0];
        target_speeds[1] = i2c_data.values[1];
      } else {
        int startIdx = cmd == 1 ? 0 : 2;
        for(int i=0; i<2; i++) {
          servo_angles[startIdx+i] = constrain(i2c_data.values[i], 0, 180);
          writeServoAngle(startIdx+i, servo_angles[startIdx+i]);
        }
      }
    }
  }
}

void setup() {
  // I2C setup
  Wire.begin(ESP32_ADDRESS);
  Wire.onReceive(receiveEvent);
  
  // Motor control pins
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  // PWM setup
  for(int i=0; i<2; i++) {
    ledcSetup(DC_channels[i], DC_freq, DC_resolution);
    ledcAttachPin((const int[]){ENA, ENB}[i], DC_channels[i]);
  }
  
  // Encoder setup
  pinMode(C1A, INPUT_PULLUP);
  pinMode(C1B, INPUT_PULLUP);
  pinMode(C2A, INPUT_PULLUP);
  pinMode(C2B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(C1A), encoder1ISR, FALLING);
  attachInterrupt(digitalPinToInterrupt(C2A), encoder2ISR, FALLING);
  
  // Servo setup
  setupServos();
  for(int i=0; i<4; i++)
    writeServoAngle(i, servo_angles[i]);
}

void loop() {
  static unsigned long lastUpdate = 0;
  if(millis() - lastUpdate >= SAMPLE_TIME_MS) {
    // Update speed calculations
    noInterrupts();
    int ticks[] = {encoder_ticks[0], encoder_ticks[1]};
    encoder_ticks[0] = encoder_ticks[1] = 0;
    interrupts();
    
    for(int i=0; i<2; i++) {
      float rpm = (ticks[i] * 60000.0) / (ENC_COUNTS_PER_REV * SAMPLE_TIME_MS);
      current_speeds[i] = speed_filters[i].update(rpm);
    }
    
    // Update PID and motor outputs
    for(int i=0; i<2; i++) {
      updatePID(i);
      updateMotorOutput(i);
    }
    
    lastUpdate = millis();
  }
}