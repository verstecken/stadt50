#include <Arduino.h>

// Verkabelung: Taster ein Bein -> GPIO, anderes -> GND (INPUT_PULLUP)
// LED: Anode -> GPIO via 330Ω, Kathode -> GND
// Taster = linke Reihe, LED = gegenüberliegende rechte Pin-Nummer
//
// Button | Taster (GPIO) | Pin | LED (GPIO) | Pin
// -------+---------------+-----+------------+-----
//   a    | GP5           |  7  | GP28       | 34
//   b    | GP6           |  9  | GP27       | 32
//   c    | GP7           | 10  | GP26       | 31
//   d    | GP9           | 12  | GP22       | 29
//   e    | GP10          | 14  | GP21       | 27
//   f    | GP11          | 15  | GP20       | 26
//   g    | GP12          | 16  | GP19       | 25
//   h    | GP13          | 17  | GP18       | 24
//   i    | GP14          | 19  | GP17       | 22
//   j    | GP15          | 20  | GP16       | 21
// GND: Pin 3, 8, 13, 18, 23, 28, 33, 38
// Pin 30 = RUN (Reset), kein GPIO
//
// Pico -> Chrome:  a-j bei Druck
// Chrome -> Pico:  X1 = alle an (Leerlauf), X0 = alle aus
//                  a1 = nur a blinkt, Rest aus; a0 = zurück zu X1 (alle an)

static const uint8_t BTN_PINS[] = {5, 6, 7, 9, 10, 11, 12, 13, 14, 15};
static const uint8_t LED_PINS[] = {28, 27, 26, 22, 21, 20, 19, 18, 17, 16};
static const char KEYS[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'};
static const int NUM = 10;

static const unsigned long DEBOUNCE_MS = 50;
static const unsigned long BLINK_MS = 400;

unsigned long lastChange[NUM] = {0};
bool lastState[NUM] = {true, true, true, true, true, true, true, true, true, true};

int blinkIndex = -1;
unsigned long lastBlink = 0;
bool ledState = false;
String serialLine = "";

int keyIndex(char k) {
  for (int i = 0; i < NUM; i++) {
    if (KEYS[i] == k) return i;
  }
  return -1;
}

void setLedSolid(int i, bool on) {
  digitalWrite(LED_PINS[i], on ? HIGH : LOW);
}

void allLedsOff() {
  blinkIndex = -1;
  for (int i = 0; i < NUM; i++) {
    setLedSolid(i, false);
  }
}

void allLedsOn() {
  blinkIndex = -1;
  for (int i = 0; i < NUM; i++) {
    setLedSolid(i, true);
  }
}

void handleSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      serialLine.trim();
      if (serialLine == "X1") {
        allLedsOn();
      } else if (serialLine == "X0" || serialLine == "V0") {
        allLedsOff();
      } else if (serialLine.length() == 2) {
        int i = keyIndex(serialLine[0]);
        if (i >= 0) {
          if (serialLine[1] == '1') {
            for (int j = 0; j < NUM; j++) {
              setLedSolid(j, false);
            }
            blinkIndex = i;
            lastBlink = 0;
            ledState = false;
          } else if (serialLine[1] == '0') {
            if (blinkIndex == i) blinkIndex = -1;
            allLedsOn();
          }
        }
      }
      serialLine = "";
    } else {
      serialLine += c;
    }
  }
}

void updateBlink(unsigned long now) {
  if (blinkIndex < 0) return;
  if (lastBlink == 0 || now - lastBlink >= BLINK_MS) {
    lastBlink = now;
    ledState = !ledState;
    digitalWrite(LED_PINS[blinkIndex], ledState ? HIGH : LOW);
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < NUM; i++) {
    pinMode(BTN_PINS[i], INPUT_PULLUP);
    pinMode(LED_PINS[i], OUTPUT);
  }
  allLedsOn();
}

void loop() {
  unsigned long now = millis();
  handleSerial();
  updateBlink(now);
  for (int i = 0; i < NUM; i++) {
    bool reading = digitalRead(BTN_PINS[i]) == HIGH;
    if (reading != lastState[i] && now - lastChange[i] >= DEBOUNCE_MS) {
      lastChange[i] = now;
      lastState[i] = reading;
      if (!reading) {
        Serial.println(String(KEYS[i]));
      }
    }
  }
}
