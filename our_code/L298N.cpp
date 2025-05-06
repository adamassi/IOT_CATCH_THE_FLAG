#include "L298N.h"

typedef void (*CallBackFunction)();

// Constructor for full speed (no PWM control, jumper on EN)
L298N::L298N(uint8_t pinIN1, uint8_t pinIN2) {
   _pinEnable = 255; // invalid pin
   _pinIN1 = pinIN1;
   _pinIN2 = pinIN2;
   _pwmVal = 255;
   _isMoving = false;
   _canMove = true;
   _lastMs = 0;
   _direction = STOP;

   pinMode(_pinIN1, OUTPUT);
   pinMode(_pinIN2, OUTPUT);
}

// Constructor for ESP32 with PWM speed control
L298N::L298N(uint8_t pinEnable, uint8_t pinIN1, uint8_t pinIN2, uint8_t pwmChannel) {
   _pinEnable = pinEnable;
   _pinIN1 = pinIN1;
   _pinIN2 = pinIN2;
   _pwmChannel = pwmChannel;
   _pwmVal = 100;
   _isMoving = false;
   _canMove = true;
   _lastMs = 0;
   _direction = STOP;

   pinMode(_pinIN1, OUTPUT);
   pinMode(_pinIN2, OUTPUT);

   // ESP32-specific PWM setup
   ledcAttachPin(_pinEnable, _pwmChannel);
   ledcSetup(_pwmChannel, 1000, 8); // 1kHz, 8-bit
}

void L298N::setSpeed(unsigned short pwmVal) {
   _pwmVal = constrain(pwmVal, 0, 255);
   //added by me
   if (_isMoving && _pinEnable != 255) {
      ledcWrite(_pwmChannel, _pwmVal);  // Live update
    }
}

unsigned short L298N::getSpeed() {
   return this->isMoving() ? _pwmVal : 0;
}

void L298N::forward() {
   digitalWrite(_pinIN1, HIGH);
   digitalWrite(_pinIN2, LOW);

   if (_pinEnable != 255) {
      ledcWrite(_pwmChannel, _pwmVal);
   }

   _direction = FORWARD;
   _isMoving = true;
}

void L298N::backward() {
   digitalWrite(_pinIN1, LOW);
   digitalWrite(_pinIN2, HIGH);

   if (_pinEnable != 255) {
      ledcWrite(_pwmChannel, _pwmVal);
   }

   _direction = BACKWARD;
   _isMoving = true;
}

void L298N::run(L298N::Direction direction) {
   switch (direction) {
      case BACKWARD:
         this->backward();
         break;
      case FORWARD:
         this->forward();
         break;
      case STOP:
      default:
         this->stop();
         break;
   }
}

void L298N::runFor(unsigned long delay, L298N::Direction direction, CallBackFunction callback) {
   if ((_lastMs == 0) && _canMove) {
      _lastMs = millis();

      switch (direction) {
         case FORWARD:
            this->forward();
            break;
         case BACKWARD:
            this->backward();
            break;
         case STOP:
         default:
            this->stop();
            break;
      }
   }

   if (((millis() - _lastMs) > delay) && _canMove) {
      this->stop();
      _lastMs = 0;
      _canMove = false;

      callback();
   }
}

void L298N::runFor(unsigned long delay, L298N::Direction direction) {
   this->runFor(delay, direction, fakeCallback);
}

void L298N::forwardFor(unsigned long delay, CallBackFunction callback) {
   this->runFor(delay, FORWARD, callback);
}

void L298N::forwardFor(unsigned long delay) {
   this->runFor(delay, FORWARD);
}

void L298N::backwardFor(unsigned long delay, CallBackFunction callback) {
   this->runFor(delay, BACKWARD, callback);
}

void L298N::backwardFor(unsigned long delay) {
   this->runFor(delay, BACKWARD);
}

void L298N::stop() {
   digitalWrite(_pinIN1, LOW);
   digitalWrite(_pinIN2, LOW);

   if (_pinEnable != 255) {
      ledcWrite(_pwmChannel, 0);
   }

   _direction = STOP;
   _isMoving = false;
}

void L298N::reset() {
   _canMove = true;
}

boolean L298N::isMoving() {
   return _isMoving;
}

L298N::Direction L298N::getDirection() {
   return _direction;
}

void L298N::fakeCallback() {}





















// /*
//   L298N.cpp - Libreria per gestire i movimenti di un motore DC con il modulo
//   L298N Autore:   Andrea Lombardo Sito web: http://www.lombardoandrea.com
// */

// #include "L298N.h"

// typedef void (*CallBackFunction)();

// L298N::L298N(uint8_t pinEnable, uint8_t pinIN1, uint8_t pinIN2) {
//   _pinEnable = pinEnable;
//   _pinIN1 = pinIN1;
//   _pinIN2 = pinIN2;
//   _pwmVal = 100;
//   _isMoving = false;
//   _canMove = true;
//   _lastMs = 0;
//   _direction = STOP;

//   pinMode(_pinEnable, OUTPUT);
//   pinMode(_pinIN1, OUTPUT);
//   pinMode(_pinIN2, OUTPUT);
// }

// L298N::L298N(uint8_t pinIN1, uint8_t pinIN2) {
//   _pinEnable = -1;
//   _pinIN1 = pinIN1;
//   _pinIN2 = pinIN2;
//   _pwmVal = 255;  // It's always at the max speed due to jumper on module
//   _isMoving = false;
//   _canMove = true;
//   _lastMs = 0;
//   _direction = STOP;

//   pinMode(_pinIN1, OUTPUT);
//   pinMode(_pinIN2, OUTPUT);
// }

// void L298N::setSpeed(unsigned short pwmVal) {
//   _pwmVal = pwmVal;
// }

// unsigned short L298N::getSpeed() {
//   return this->isMoving() ? _pwmVal : 0;
// }

// void L298N::forward() {
//   digitalWrite(_pinIN1, HIGH);
//   digitalWrite(_pinIN2, LOW);

//   analogWrite(_pinEnable, _pwmVal);

//   _direction = FORWARD;
//   _isMoving = true;
// }

// void L298N::backward() {
//   digitalWrite(_pinIN1, LOW);
//   digitalWrite(_pinIN2, HIGH);

//   analogWrite(_pinEnable, _pwmVal);

//   _direction = BACKWARD;
//   _isMoving = true;
// }

// void L298N::run(L298N::Direction direction) {
//   switch (direction) {
//     case BACKWARD:
//       this->backward();
//       break;
//     case FORWARD:
//       this->forward();
//       break;
//     case STOP:
//       this->stop();
//       break;
//   }
// }

// // Timing and callback

// void L298N::runFor(unsigned long delay,
//                    L298N::Direction direction,
//                    CallBackFunction callback) {
//   if ((_lastMs == 0) && _canMove) {
//     _lastMs = millis();

//     switch (direction) {
//       case FORWARD:
//         this->forward();
//         break;
//       case BACKWARD:
//         this->backward();
//         break;
//       case STOP:
//       default:
//         this->stop();
//         break;
//     }
//   }

//   if (((millis() - _lastMs) > delay) && _canMove) {
//     this->stop();
//     _lastMs = 0;
//     _canMove = false;

//     callback();
//   }
// }

// void L298N::runFor(unsigned long delay, L298N::Direction direction) {
//   this->runFor(delay, direction, fakeCallback);
// }

// void L298N::forwardFor(unsigned long delay, CallBackFunction callback) {
//   this->runFor(delay, FORWARD, callback);
// }

// void L298N::forwardFor(unsigned long delay) {
//   this->runFor(delay, FORWARD);
// }

// void L298N::backwardFor(unsigned long delay, CallBackFunction callback) {
//   this->runFor(delay, BACKWARD, callback);
// }

// void L298N::backwardFor(unsigned long delay) {
//   this->runFor(delay, BACKWARD);
// }

// void L298N::stop() {
//   digitalWrite(_pinIN1, LOW);
//   digitalWrite(_pinIN2, LOW);

//   analogWrite(_pinEnable, 255);

//   _direction = STOP;
//   _isMoving = false;
// }

// void L298N::reset() {
//   _canMove = true;
// }

// boolean L298N::isMoving() {
//   return _isMoving;
// }

// L298N::Direction L298N::getDirection() {
//   return _direction;
// }

// void L298N::fakeCallback() {}