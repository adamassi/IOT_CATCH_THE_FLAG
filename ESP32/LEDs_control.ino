// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// Released under the GPLv3 license to match the rest of the
// Adafruit NeoPixel library

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN        12// On Trinket or Gemma, suggest changing this to 1
#define LED_PINN 2 
// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS 6 // Popular NeoPixel ring size

// When setting up the NeoPixel library, we tell it how many pixels,
// and which pin to use to send signals. Note that for older NeoPixel
// strips you might need to change the third parameter -- see the
// strandtest example for more information on possible values.
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

#define DELAYVAL 100 // Time (in milliseconds) to pause between pixels

void setup() {
  pinMode(LED_PINN, OUTPUT);
  // These lines are specifically to support the Adafruit Trinket 5V 16 MHz.
  // Any other board, you can remove this part (but no harm leaving it):
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  // END of Trinket-specific code.

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
}

void loop() {
  


  pixels.clear(); // Set all pixel colors to 'off'

  // The first NeoPixel in a strand is #0, second is 1, all the way up
  // to the count of pixels minus one.
  for(int i=0; i<NUMPIXELS; i++) { // For each pixel...
    delay(DELAYVAL);
    // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    // Here we're using a moderately bright green color:
    pixels.setPixelColor(i, pixels.Color(i*20, 100, i*20));

    pixels.show();   // Send the updated pixel colors to the hardware.

    delay(DELAYVAL); // Pause before next pass through loop
  }
}





// #include <Adafruit_NeoPixel.h>

// #ifdef __AVR__
//   #include <avr/power.h>
// #endif

// #define PIN        12
// #define LED_PINN   2
// #define NUMPIXELS  6

// Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// int brightness = 80;

// void setup() {
//   pinMode(LED_PINN, OUTPUT);

// #if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
//   clock_prescale_set(clock_div_1);
// #endif

//   pixels.begin();
//   pixels.setBrightness(brightness);
//   pixels.clear();
//   pixels.show();
// }

// void loop() {
//   rainbowSpin(4);
//   sparkle(40);
//   colorWipe(pixels.Color(255, 0, 0), 80);
//   colorWipe(pixels.Color(0, 255, 0), 80);
//   colorWipe(pixels.Color(0, 0, 255), 80);
//   theaterChaseRainbow(3);
//   breatheColor(pixels.Color(255, 0, 150), 2);
// }

// // Creates rainbow colors
// uint32_t wheel(byte pos) {
//   pos = 255 - pos;

//   if (pos < 85) {
//     return pixels.Color(255 - pos * 3, 0, pos * 3);
//   }

//   if (pos < 170) {
//     pos -= 85;
//     return pixels.Color(0, pos * 3, 255 - pos * 3);
//   }

//   pos -= 170;
//   return pixels.Color(pos * 3, 255 - pos * 3, 0);
// }

// // Smooth spinning rainbow
// void rainbowSpin(int cycles) {
//   for (int j = 0; j < 256 * cycles; j++) {
//     for (int i = 0; i < NUMPIXELS; i++) {
//       int colorIndex = (i * 256 / NUMPIXELS + j) & 255;
//       pixels.setPixelColor(i, wheel(colorIndex));
//     }

//     pixels.show();
//     delay(20);
//   }
// }

// // Random colorful sparkle effect
// void sparkle(int flashes) {
//   pixels.clear();

//   for (int i = 0; i < flashes; i++) {
//     int led = random(NUMPIXELS);

//     int r = random(50, 256);
//     int g = random(50, 256);
//     int b = random(50, 256);

//     pixels.setPixelColor(led, pixels.Color(r, g, b));
//     pixels.show();

//     delay(80);

//     pixels.setPixelColor(led, pixels.Color(0, 0, 0));
//     pixels.show();

//     delay(40);
//   }
// }

// // One-by-one color fill
// void colorWipe(uint32_t color, int wait) {
//   pixels.clear();

//   for (int i = 0; i < NUMPIXELS; i++) {
//     pixels.setPixelColor(i, color);
//     pixels.show();
//     delay(wait);
//   }

//   delay(300);
// }

// // Theater chase with rainbow colors
// void theaterChaseRainbow(int cycles) {
//   for (int j = 0; j < 256 * cycles; j++) {
//     for (int q = 0; q < 3; q++) {
//       pixels.clear();

//       for (int i = 0; i < NUMPIXELS; i += 3) {
//         int pixel = i + q;

//         if (pixel < NUMPIXELS) {
//           pixels.setPixelColor(pixel, wheel((i + j) % 255));
//         }
//       }

//       pixels.show();
//       delay(90);
//     }
//   }
// }

// // Breathing / fading color effect
// void breatheColor(uint32_t color, int cycles) {
//   for (int c = 0; c < cycles; c++) {
//     for (int b = 10; b <= 120; b += 3) {
//       pixels.setBrightness(b);

//       for (int i = 0; i < NUMPIXELS; i++) {
//         pixels.setPixelColor(i, color);
//       }

//       pixels.show();
//       delay(25);
//     }

//     for (int b = 120; b >= 10; b -= 3) {
//       pixels.setBrightness(b);

//       for (int i = 0; i < NUMPIXELS; i++) {
//         pixels.setPixelColor(i, color);
//       }

//       pixels.show();
//       delay(25);
//     }
//   }

//   pixels.setBrightness(brightness);
// }

