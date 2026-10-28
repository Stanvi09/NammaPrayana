#define IR1 25
#define IR3 26

// =====================================
// EXPECTED TRAVEL TIMES
// =====================================

const float expectedLoopTime = 16.22;   // Station 1 → Station 1
const float expectedS1toS3 = 4.00;      // Station 1 → Station 3


// =====================================
// SENSOR SETTINGS
// =====================================

// Prevent the same train from being detected repeatedly
const unsigned long sensorBuffer = 6000;

// Station 3 detection must be at least
// 2.5 seconds after Station 1
const unsigned long minimumS1toS3 = 2500;

// Station 1 must be at least 12 seconds
// away from the previous Station 1 detection
const unsigned long minimumLoopTime = 12000;


// =====================================
// SYSTEM STATES
// =====================================

enum State {

  WAITING_FOR_FIRST_S1,

  MEASURING_LOOP,

  MEASURING_S1_TO_S3,

  WAITING_FOR_NEXT_S1
};

State currentState = WAITING_FOR_FIRST_S1;


// =====================================
// TIMING VARIABLES
// =====================================

unsigned long startTime = 0;

unsigned long lastIR1Detection = 0;
unsigned long lastIR3Detection = 0;


// =====================================
// SETUP
// =====================================

void setup() {

  Serial.begin(115200);

  pinMode(IR1, INPUT);
  pinMode(IR3, INPUT);

  Serial.println();
  Serial.println("====================================");
  Serial.println("       METRO DELAY MONITOR");
  Serial.println("====================================");

  Serial.println("Station 1 -> GPIO 25");
  Serial.println("Station 3 -> GPIO 26");

  Serial.println();

  Serial.print("Expected S1 -> S1 : ");
  Serial.print(expectedLoopTime, 2);
  Serial.println(" seconds");

  Serial.print("Expected S1 -> S3 : ");
  Serial.print(expectedS1toS3, 2);
  Serial.println(" seconds");

  Serial.println();

  Serial.println("Waiting for first Station 1...");
}


// =====================================
// MAIN LOOP
// =====================================

void loop() {

  int ir1 = digitalRead(IR1);
  int ir3 = digitalRead(IR3);

  unsigned long currentTime = millis();


  // ===================================
  // STATION 1
  // ===================================

  if (ir1 == LOW &&
      currentTime - lastIR1Detection >= sensorBuffer) {

    lastIR1Detection = currentTime;


    // ---------------------------------
    // FIRST STATION 1 DETECTION
    // ---------------------------------

    if (currentState == WAITING_FOR_FIRST_S1) {

      startTime = currentTime;

      currentState = MEASURING_LOOP;

      Serial.println();
      Serial.println("========== STATION 1 ==========");
      Serial.println("Train detected.");
      Serial.println("Full loop timer STARTED.");
      Serial.println("===============================");
    }


    // ---------------------------------
    // TRAIN RETURNS TO STATION 1
    // ---------------------------------

    else if (currentState == MEASURING_LOOP) {

      unsigned long elapsed =
        currentTime - startTime;


      // Ignore duplicate / garbage detection
      if (elapsed >= minimumLoopTime) {

        float actualLoopTime =
          elapsed / 1000.0;

        float loopDelay =
          actualLoopTime - expectedLoopTime;


        Serial.println();
        Serial.println("========== STATION 1 ==========");

        Serial.print("Expected time : ");
        Serial.print(expectedLoopTime, 2);
        Serial.println(" s");

        Serial.print("Actual time   : ");
        Serial.print(actualLoopTime, 2);
        Serial.println(" s");

        Serial.print("Delay         : ");
        Serial.print(loopDelay, 2);
        Serial.println(" s");

        Serial.println("===============================");


        // ---------------------------------
        // START S1 → S3 TIMER
        // ---------------------------------

        startTime = currentTime;

        currentState = MEASURING_S1_TO_S3;

        Serial.println();
        Serial.println("Now measuring Station 1 -> Station 3...");
      }

      else {

        Serial.print("Ignored Station 1 detection at ");
        Serial.print(elapsed / 1000.0, 2);
        Serial.println(" s");
      }
    }


    // ---------------------------------
    // RETURN TO STATION 1 AFTER S3
    // ---------------------------------

    else if (currentState == WAITING_FOR_NEXT_S1) {

      startTime = currentTime;

      currentState = MEASURING_LOOP;

      Serial.println();
      Serial.println("========== STATION 1 ==========");
      Serial.println("New full loop timer STARTED.");
      Serial.println("===============================");
    }
  }


  // ===================================
  // STATION 3
  // ===================================

  if (ir3 == LOW &&
      currentState == MEASURING_S1_TO_S3 &&
      currentTime - lastIR3Detection >= sensorBuffer) {

    lastIR3Detection = currentTime;


    unsigned long elapsed =
      currentTime - startTime;


    // ---------------------------------
    // IGNORE DETECTION BEFORE 2.5 SEC
    // ---------------------------------

    if (elapsed >= minimumS1toS3) {

      float actualTravelTime =
        elapsed / 1000.0;

      float station3Delay =
        actualTravelTime - expectedS1toS3;


      Serial.println();
      Serial.println("========== STATION 3 ==========");

      Serial.print("Expected time : ");
      Serial.print(expectedS1toS3, 2);
      Serial.println(" s");

      Serial.print("Actual time   : ");
      Serial.print(actualTravelTime, 2);
      Serial.println(" s");

      Serial.print("Delay         : ");
      Serial.print(station3Delay, 2);
      Serial.println(" s");

      Serial.println("===============================");


      // ---------------------------------
      // STATION 3 COMPLETE
      // ---------------------------------

      currentState = WAITING_FOR_NEXT_S1;

      Serial.println();
      Serial.println("Waiting for train to return to Station 1...");
    }

    else {

      Serial.print("Ignored Station 3 detection at ");
      Serial.print(elapsed / 1000.0, 2);
      Serial.println(" s");
    }
  }
}
