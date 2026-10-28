const int SENSOR_A = 32;       // outer sensor
const int SENSOR_B = 33;       // inner sensor
const int MAX_OCCUPANCY = 10;

const unsigned long TIMEOUT_MS = 3000;  // give up if the 2nd sensor never fires
const unsigned long CLEAR_MS   = 40;    // both sensors clear this long = ready again

enum State { IDLE, A_FIRST, B_FIRST, WAIT_CLEAR };
State state = IDLE;

int count = 0;
unsigned long stateStart = 0;
unsigned long clearSince = 0;

// Sensor reads as active only if LOW on 2 reads in a row (filters noise, still fast)
bool active(int pin) {
  if (digitalRead(pin) != LOW) return false;
  delayMicroseconds(500);
  return digitalRead(pin) == LOW;
}

void setup() {
  Serial.begin(115200);
  pinMode(SENSOR_A, INPUT);
  pinMode(SENSOR_B, INPUT);
  Serial.println("Ready. Count = 0");
}

void loop() {
  bool a = active(SENSOR_A);
  bool b = active(SENSOR_B);

  switch (state) {

    case IDLE:
      if (a && !b)      { state = A_FIRST; stateStart = millis(); }
      else if (b && !a) { state = B_FIRST; stateStart = millis(); }
      // if both fire at the same instant, we ignore it and wait for a clear order
      break;

    case A_FIRST:                       // A already seen, repeated A is ignored
      if (b) {                          // A then B = person entered
        if (count < MAX_OCCUPANCY) count++;
        else Serial.println("FULL: max occupancy reached");
        Serial.println("IN");
        report();
        state = WAIT_CLEAR;
        clearSince = 0;
      } else if (millis() - stateStart > TIMEOUT_MS) {
        state = IDLE;
      }
      break;

    case B_FIRST:                       // B already seen, repeated B is ignored
      if (a) {                          // B then A = person exited
        if (count > 0) count--;
        Serial.println("OUT");
        report();
        state = WAIT_CLEAR;
        clearSince = 0;
      } else if (millis() - stateStart > TIMEOUT_MS) {
        state = IDLE;
      }
      break;

    case WAIT_CLEAR:                    // wait until the person has fully passed
      if (!a && !b) {
        if (clearSince == 0) clearSince = millis();
        if (millis() - clearSince > CLEAR_MS) state = IDLE;
      } else {
        clearSince = 0;
      }
      break;
  }

  delay(1);   // check the sensors about 1000 times per second
}

void report() {
  float pct = 100.0 * count / MAX_OCCUPANCY;
  const char* level = pct < 33 ? "LOW" : (pct < 66 ? "MEDIUM" : "HIGH");
  Serial.printf("Count: %d/%d  (%.0f%%)  Level: %s\n", count, MAX_OCCUPANCY, pct, level);
}
