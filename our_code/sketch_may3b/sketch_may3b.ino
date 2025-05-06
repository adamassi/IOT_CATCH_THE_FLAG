// #include <L298NX2.h>



// /*********************
// //  IN1 + IN2 Right Side
// //  IN3 + IN4 Left  Side
// //  IN2 + IN3 HIGH => Forward
// //  5V for enable / controll speed for both sides together
// **********************/


// // Speed Pin
// const unsigned int EN1 = 14;
// const unsigned int EN2 = 14;
// const unsigned int motorPWMChannel = 1;

// // Motors Pin definition
// const unsigned int IN1 = 27;
// const unsigned int IN2 = 26;

// const unsigned int IN3 = 25;
// const unsigned int IN4 = 33;

// L298NX2 motors(EN1, IN2, IN1, EN2, IN3, IN4);

// void setup() {
//   Serial.begin(115200);
// motors.forward();
// delay(3000);
// Serial.println("next 120");
// motors.setSpeed(120);
// delay(3000);
// Serial.println("next 250");
// motors.setSpeed(250);
// delay(3000);
// Serial.println("next 0");
// motors.setSpeed(0);


// }

// void loop() {
//   // put your main code here, to run repeatedly:

// }








// #include <L298N.h>

// L298N motor(14, 27, 26);  // EN, IN1, IN2

// void setup() {
//   Serial.begin(115200);
//   Serial.println("started");
//   motor.forward();
//   delay(3000);
//   Serial.println("next 120");
//   motor.setSpeed(120);
//   delay(3000);
//   Serial.println("next 250");
//   motor.setSpeed(250);
//   delay(3000);
//   Serial.println("next 0");
//   motor.setSpeed(0);
// }


// void loop() {
// //   // put your main code here, to run repeatedly:

// }









// const int ENA = 14;      // PWM speed control
// const int IN1 = 27;      // Direction control
// const int IN2 = 26;

// void setup() {
//   Serial.begin(115200);

//   pinMode(IN1, OUTPUT);
//   pinMode(IN2, OUTPUT);

//   // PWM setup for ESP32
//   ledcAttachPin(ENA, 0);          // Attach pin 14 to channel 0
//   ledcSetup(0, 1000, 8);          // 1 kHz PWM, 8-bit resolution

//   // Forward direction
//   digitalWrite(IN1, HIGH);
//   digitalWrite(IN2, LOW);

//   Serial.println("Speed: 255");
//   ledcWrite(0, 255);  // Full speed
//   delay(3000);

//   Serial.println("Speed: 120");
//   ledcWrite(0, 120);  // Medium speed
//   delay(3000);

//   Serial.println("Speed: 250");
//   ledcWrite(0, 250);  // High speed
//   delay(3000);

//   Serial.println("Stop");
//   ledcWrite(0, 0);    // Stop
// }

// void loop() {
//   // Nothing here
// }





// #include "L298N.h"

// // Motor wiring:
// // ENA = GPIO 14 (PWM)
// // IN1 = GPIO 27
// // IN2 = GPIO 26
// // PWM channel = 0

// L298N motor(14, 27, 26, 0); // (EN, IN1, IN2, PWM channel)

// void setup() {
//   Serial.begin(115200);
//   delay(1000);  // Allow time to open Serial Monitor

//   Serial.println("Starting motor test...");

//   // Set initial speed and go forward
//   motor.setSpeed(100);
//   Serial.println("Motor FORWARD at speed 100");
//   motor.forward();
//   delay(3000);

//   // Change speed
//   motor.setSpeed(20);
//   //motor.forward();
//   Serial.println("Motor speed changed to 20");
//   delay(3000);

//   // Change speed
//   motor.setSpeed(200);
//   //motor.forward();
//   Serial.println("Motor speed changed to 200");
//   delay(3000);

//   // Set to maximum
//   motor.setSpeed(255);
//   //motor.forward();
//   Serial.println("Motor speed changed to 255 (full)");
//   delay(3000);

//   // Stop the motor
//   motor.stop();
//   Serial.println("Motor STOPPED");
// }

// void loop() {
//   // Nothing here
// }








// const int ENA = 14;      // PWM
// const int IN1 = 27;
// const int IN2 = 26;

// void setup() {
//   Serial.begin(115200);

//   pinMode(IN1, OUTPUT);
//   pinMode(IN2, OUTPUT);

//   ledcAttachPin(ENA, 0);
//   ledcSetup(0, 1000, 8);  // Channel 0, 1kHz, 8-bit

//   digitalWrite(IN1, HIGH);
//   digitalWrite(IN2, LOW);

//   Serial.println("Speed = 100");
//   ledcWrite(0, 100);
//   delay(3000);

//   Serial.println("Speed = 200");
//   ledcWrite(0, 200);
//   delay(3000);

//   Serial.println("Speed = 255 (max)");
//   ledcWrite(0, 255);
//   delay(3000);

//   Serial.println("Speed = 0 (stop)");
//   ledcWrite(0, 0);
// }

// void loop() {}





#include "L298NX2.h"

// Shared EN pin and shared PWM channel
#define EN_SHARED 14
#define PWM_CHANNEL 0

// Motor A control pins
#define IN1_A 27
#define IN2_A 26

// Motor B control pins
#define IN1_B 25
#define IN2_B 33

// Create L298NX2 object with shared EN pin and PWM channel
L298NX2 motors(
  EN_SHARED, IN2_A, IN1_A, PWM_CHANNEL,
  EN_SHARED, IN1_B, IN2_B, PWM_CHANNEL
);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting two-motor test with shared EN...");

  motors.setSpeed(100);
  Serial.println("FORWARD at speed 100");
  motors.forward();
  delay(3000);

  motors.setSpeed(200);
  Serial.println("Speed changed to 200");
  motors.forwardA();  // Required to apply the new speed
  motors.backwardB();
  delay(3000);

  motors.setSpeed(255);
  Serial.println("Speed changed to 255");
  motors.forwardB();  // Apply again
  motors.backwardA();
  delay(3000);

  motors.stop();
  Serial.println("Motors stopped");
}

void loop() {
  // Nothing here
}

