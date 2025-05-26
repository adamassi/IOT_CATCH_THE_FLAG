#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ESP32Servo.h>


Servo myServo;



const char *ssid = "IOT_project";     //remember to change
const char *password = "Arduino123";  //remember to change

int ENA_pin = 13;

int IN1 = 27;
int IN2 = 26;
int IN3 = 25;
int IN4 = 33;

const int servoPin = 15;


String slider_value = "0";
int pwm_power_value = 45;

int servoAngle = 10;

const int frequency = 500;

const int pwm_channel = 1;
// const int servo_channel = 1;
const int resolution = 8;

const char *input_parameter = "value";

AsyncWebServer server(80);

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DC Motor Speed Control Web Server</title>
  <style>
    html {font-family: Times New Roman; display: inline-block; text-align: center;}
    h2 {font-size: 2.3rem;}
    p {font-size: 2.0rem;}
    body {max-width: 400px; margin:0px auto; padding-bottom: 25px;}
    .slider { -webkit-appearance: none; margin: 14px; width: 360px; height: 25px; background: #4000ff;
      outline: none; -webkit-transition: .2s; transition: opacity .2s;}
    .slider::-webkit-slider-thumb {-webkit-appearance: none; appearance: none; width: 35px; height: 35px; background:#01070a; cursor: pointer;}
    .slider::-moz-range-thumb { width: 35px; height: 35px; background: #01070a; cursor: pointer; } 
    .btn {padding: 16px 24px; margin: 10px; font-size: 18px; background-color: #008CBA; color: white; border: none; cursor: pointer; border-radius: 8px;}
    .btn:hover {background-color: #005f73;}
  </style>
</head>
<body>
  <h2>DC Motor Speed Control Web Server</h2>
  <p><span id="textslider_value">%SLIDERVALUE%</span></p>
  <p><input type="range" onchange="updateSliderPWM(this)" id="pwmSlider" min="-255" max="255" value="%SLIDERVALUE%" step="1" class="slider"></p>
  
  <p><strong>PWM Power</strong></p>
  <p><span id="pwm_power_display">%SLIDERPWMVALUE%</span></p>
  <input type="range" onchange="updatePWMSlider(this)" id="pwmPowerSlider" min="0" max="255" value="%SLIDERPWMVALUE%" step="1" class="slider">
  

  <p>
    <button class="btn" onclick="goForward()">Forward</button><br>
    <button class="btn" onclick="turnLeft()">Left</button>
    <button class="btn" onclick="stopMotor()">Stop</button>
    <button class="btn" onclick="turnRight()">Right</button><br>
    <button class="btn" onclick="goBackward()">Backward</button>
  </p>

<script>
function updateSliderPWM(element) {
  var slider_value = document.getElementById("pwmSlider").value;
  document.getElementById("textslider_value").innerHTML = slider_value;
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/slider?value=" + slider_value, true);
  xhr.send();
}

function updatePWMSlider(element) {
  var pwm_value = document.getElementById("pwmPowerSlider").value;
  document.getElementById("pwm_power_display").innerHTML = pwm_value;
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/set_pwm_power?value=" + pwm_value, true);
  xhr.send();
}

function stopMotor() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/stop", true);
  xhr.send();
  document.getElementById("pwmSlider").value = 0;
  document.getElementById("textslider_value").innerHTML = 0;
}

function goForward() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/go", true);
  xhr.send();
}

function goBackward() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/back", true);
  xhr.send();
}

function turnLeft() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/left", true);
  xhr.send();
}

function turnRight() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/right", true);
  xhr.send();
}
</script>
</body>
</html>
)rawliteral";


// String processor(const String &var) {
//   if (var == "SLIDERVALUE") {
//     return slider_value;
//   }
//   return String();
// }

String processor(const String &var) {
  if (var == "SLIDERVALUE") {
    return slider_value;
  } else if (var == "SLIDERPWMVALUE") {
    return String(pwm_power_value);
  }
  return String();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(ENA_pin, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  ledcSetup(pwm_channel, frequency, resolution);
  ledcAttachPin(ENA_pin, pwm_channel);
  ledcWrite(pwm_channel, 0);  // Start with motor stopped
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  // ledcSetup(servo_channel, frequency, resolution);
  // ledcAttachPin(servoPin, servo_channel);
  myServo.attach(servoPin);
  

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }

  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send_P(200, "text/html", index_html, processor);
  });



  server.on("/slider", HTTP_GET, [](AsyncWebServerRequest *request) {
    String message;
    if (request->hasParam(input_parameter)) {
      message = request->getParam(input_parameter)->value();
      slider_value = message;

      int val = slider_value.toInt();
      int pwm_value = abs(val);  // Always a positive PWM

      // Determine motor direction
      if (val > 0) {
        // Forward
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, HIGH);
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);

      } else if (val < 0) {
        // Reverse
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, HIGH);
      } else {
        // Stop
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, LOW);
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, LOW);
      }

      ledcWrite(pwm_channel, pwm_value);  // Apply PWM regardless of direction
    } else {
      message = "No message sent";
    }
    Serial.println(message);
    request->send(200, "text/plain", "OK");
  });

  server.on("/set_pwm_power", HTTP_GET, [](AsyncWebServerRequest *request) {
  if (request->hasParam(input_parameter)) {
    pwm_power_value = request->getParam(input_parameter)->value().toInt();
    Serial.print("PWM power updated: ");
    Serial.println(pwm_power_value);
  }
  request->send(200, "text/plain", "PWM power updated");
});

  server.on("/stop", HTTP_GET, [](AsyncWebServerRequest *request) {
    //slider_value = "0";
    ledcWrite(pwm_channel, 0);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    request->send(200, "text/plain", "Motor stopped");
  });

  server.on("/go", HTTP_GET, [](AsyncWebServerRequest *request) {
    //slider_value = "150";
    ledcWrite(pwm_channel, 250);

    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);

    request->send(200, "text/plain", "Motor go");
  });

  server.on("/back", HTTP_GET, [](AsyncWebServerRequest *request) {
    //slider_value = "150";
    ledcWrite(pwm_channel, 250);
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    request->send(200, "text/plain", "Back");
  });

  server.on("/right", HTTP_GET, [](AsyncWebServerRequest *request) {
    //slider_value = "150";
    int speed = pwm_power_value;
    if (request->hasParam(input_parameter)) {
      speed = request->getParam(input_parameter)->value().toInt();
    }
    ledcWrite(pwm_channel, speed);
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    request->send(200, "text/plain", "turn right");
  });

  server.on("/left", HTTP_GET, [](AsyncWebServerRequest *request) {
    //slider_value = "150";
    int speed = pwm_power_value;
    if (request->hasParam(input_parameter)) {
      speed = request->getParam(input_parameter)->value().toInt();
    }
    ledcWrite(pwm_channel, speed);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);

    request->send(200, "text/plain", "turn left");
  });

  server.on("/servo", HTTP_GET, [](AsyncWebServerRequest *request) {
    if (request->hasParam(input_parameter)) {
      int angle = request->getParam(input_parameter)->value().toInt();
      angle = constrain(angle, 0, 90);  // Ensure within valid range
      myServo.write(angle);
      servoAngle = angle;
      Serial.printf("Servo angle set to: %d\n", angle);
      request->send(200, "text/plain", "Servo angle set to " + String(angle));
    } else {
      request->send(400, "text/plain", "Missing angle parameter");
    }
  });







  server.begin();
}

void loop() {
  // No need for code here
}
