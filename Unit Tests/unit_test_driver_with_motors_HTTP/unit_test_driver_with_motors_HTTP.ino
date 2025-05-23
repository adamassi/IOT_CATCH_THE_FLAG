#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

const char* ssid = "IOT_project"; //remember to change
const char* password = "Arduino123"; //remember to change

int ENA_pin = 13;
int IN1 = 26;
int IN2 = 27;
int IN3 = 24;
int IN4 = 25;


String slider_value = "0";

const int frequency = 500;
const int pwm_channel = 0;
const int resolution = 8;

const char* input_parameter = "value";

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


// const char index_html[] PROGMEM = R"rawliteral(
  
// <!DOCTYPE HTML><html>
// <head>
//   <meta name="viewport" content="width=device-width, initial-scale=1">
//   <title>DC Motor Speed Control Web Server</title>
//   <style>
//     html {font-family: Times New Roman; display: inline-block; text-align: center;}
//     h2 {font-size: 2.3rem;}
//     p {font-size: 2.0rem;}
//     body {max-width: 400px; margin:0px auto; padding-bottom: 25px;}
//     .slider { -webkit-appearance: none; margin: 14px; width: 360px; height: 25px; background: #4000ff;
//       outline: none; -webkit-transition: .2s; transition: opacity .2s;}
//     .slider::-webkit-slider-thumb {-webkit-appearance: none; appearance: none; width: 35px; height: 35px; background:#01070a; cursor: pointer;}
//     .slider::-moz-range-thumb { width: 35px; height: 35px; background: #01070a; cursor: pointer; } 
//   </style>
// </head>
// <body>
//   <h2>DC Motor Speed Control Web Server</h2>
//   <p><span id="textslider_value">%SLIDERVALUE%</span></p>
//   <p><input type="range" onchange="updateSliderPWM(this)" id="pwmSlider" min="-255" max="255" value="%SLIDERVALUE%" step="1" class="slider"></p>

// <p><button onclick="stopMotor()">Stop Motor</button></p>

// <script>
// function updateSliderPWM(element) {
//   var slider_value = document.getElementById("pwmSlider").value;
//   document.getElementById("textslider_value").innerHTML = slider_value;
//   var xhr = new XMLHttpRequest();
//   xhr.open("GET", "/slider?value="+slider_value, true);
//   xhr.send();
// }

// function stopMotor() {
//   var xhr = new XMLHttpRequest();
//   xhr.open("GET", "/stop", true);
//   xhr.send();
//   document.getElementById("pwmSlider").value = 0;
//   document.getElementById("textslider_value").innerHTML = 0;
// }
// </script>
// </body>
// </html>
// )rawliteral";

String processor(const String& var){
  if (var == "SLIDERVALUE"){
    return slider_value;
  }
  return String();
}

void setup(){
  Serial.begin(115200);
  delay(1000);
  pinMode(ENA_pin, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  ledcSetup(pwm_channel, frequency, resolution);
  ledcAttachPin(ENA_pin, pwm_channel);
  ledcWrite(pwm_channel, 0); // Start with motor stopped
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }

  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html, processor);
  });



server.on("/slider", HTTP_GET, [] (AsyncWebServerRequest *request) {
  String message;
  if (request->hasParam(input_parameter)) {
    message = request->getParam(input_parameter)->value();
    slider_value = message;

    int val = slider_value.toInt();
    int pwm_value = abs(val);  // Always a positive PWM

    // Determine motor direction
    if (val > 0) {
      // Forward
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);

    } else if (val < 0) {
      // Reverse
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
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

  server.on("/stop", HTTP_GET, [](AsyncWebServerRequest *request){
  slider_value = "0";
  ledcWrite(pwm_channel, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  request->send(200, "text/plain", "Motor stopped");
});

server.on("/go", HTTP_GET, [](AsyncWebServerRequest *request){
  slider_value = "150";
  ledcWrite(pwm_channel, 0);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN4, LOW);
  digitalWrite(IN3, HIGH);
  
  request->send(200, "text/plain", "Motor go");
});

server.on("/back", HTTP_GET, [](AsyncWebServerRequest *request){
  slider_value = "150";
  ledcWrite(pwm_channel, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  request->send(200, "text/plain", "Motor go");
});

server.on("/right", HTTP_GET, [](AsyncWebServerRequest *request){
  slider_value = "150";
  ledcWrite(pwm_channel, 0);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  request->send(200, "text/plain", "turn right");
});

server.on("/left", HTTP_GET, [](AsyncWebServerRequest *request){
  slider_value = "150";
  ledcWrite(pwm_channel, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  request->send(200, "text/plain", "turn left");
});

  Serial.println(message);
  request->send(200, "text/plain", "OK");
});






  server.begin();
}

void loop() {
  // No need for code here
}
