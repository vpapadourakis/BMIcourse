// Include the AccelStepper Library
#include <AccelStepper.h>

#define DEBUG 0

// Define step constant
#define MotorInterfaceType 4

int analogPin = A0;  
const int buttonPin = 4;
bool min_analog_calibrated = 0;

const int ledPin = 13;

int min_analog = 2; //0
int max_analog = 1022; //1023
int input_range = max_analog-min_analog;

int closed_position = -1600; //calibrate such that we get this when claw is closed
unsigned long startTime = millis();

float smoothed_input = 0; // Initial smoothed value
float weight = 0.001;

// Creates an instance
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
//AccelStepper myStepper(MotorInterfaceType, 8, 10, 9, 11);
AccelStepper myStepper(MotorInterfaceType, 9, 8, 10, 11);

void setup() {

  pinMode(buttonPin, INPUT);
  pinMode(ledPin, OUTPUT);

  // set the maximum speed, acceleration factor,
  // initial speed and the target position
  myStepper.setMaxSpeed(3000.0);
  myStepper.setAcceleration(500.0);
  myStepper.setSpeed(600); // This is only used if you use runSpeed()
  
  Serial.begin(9600);  //  setup serial
  startTime = millis();
}

float smoothData(float sensorValue, float prevSmoothedValue, float weight) {
    return weight * sensorValue + (1 - weight) * prevSmoothedValue;
}

void loop() {  
  // unsigned long elapsed = millis() - startTime;
  // if (elapsed < 10000) {

    int calibration_switch = digitalRead(buttonPin); // Read digital input (HIGH or LOW)
    // int analog_input = analogRead(analogPin);  // 0 to 1023

    if (calibration_switch == HIGH) {  
      digitalWrite(ledPin, HIGH);  // Turn LED on

      if (!min_analog_calibrated){
        static unsigned long calibration_time = millis();
        while(millis()<calibration_time+2000){
          int analog_input = analogRead(analogPin);
          analog_input = abs(analog_input);
          smoothed_input = smoothData(float(analog_input), smoothed_input, weight);
        }
        min_analog_calibrated = 1;
        min_analog = floor(smoothed_input);
        Serial.println(
          "set minimum input to: " + String(min_analog)
        );
        max_analog = 0;
      }
      
      int analog_input = analogRead(analogPin);
      analog_input = abs(analog_input);
      smoothed_input = smoothData(float(analog_input), smoothed_input, weight);
      analog_input = floor(smoothed_input);

      max_analog = max(max_analog,analog_input);
      static unsigned long lastPrint = 0;
      if (millis() - lastPrint >= 1000) {
        lastPrint = millis();
        Serial.println(
          "set max input to : " + String(max_analog)
        );
      }

      input_range = max_analog-min_analog;  
      myStepper.setCurrentPosition(0);

    }
    else{ // RUN MODE
      digitalWrite(ledPin, LOW);

      int analog_input = analogRead(analogPin);
      analog_input = abs(analog_input);
      smoothed_input = smoothData(float(analog_input), smoothed_input, weight);
      analog_input = floor(smoothed_input);

      // cut values lower than min or higher than max and set minimum to zero
      analog_input = max(min_analog,analog_input);
      analog_input = min(max_analog,analog_input);
      analog_input = analog_input - min_analog;

      long stepperPosition = myStepper.currentPosition();
      int desiredPosition = (analog_input / float(input_range)) * closed_position;
      myStepper.moveTo(desiredPosition);
      myStepper.run();

      // Optional: Print debug info
    static unsigned long lastPrint = 0;
    if (millis() - lastPrint >= 1000) {
      lastPrint = millis();
      Serial.println(
        "analog: " + String(analog_input) +
        "/" + String(input_range) +
        ", stepperPos: " + String(stepperPosition) +
        ", desiredPos: " + String(desiredPosition) +
        "/" + String(closed_position) +
        ", calibration: " + String(calibration_switch)
      );
    }

    }
    
  // }// if to stop program after x seconds (for debug)
}  //loop



//  val =0;
// val2 = 0;
// for (j=0; j<2000; j++){
//     val = val + analogRead(analogPin);  // read the input pin
//     val2 = val2 + digitalRead(inPin);   // read the inpu t pin
// }
// val = val/2000;
// val2 = val2/2000;
// Serial.print(val2);
// Serial.print("  ---   ");
//     Serial.println(val );          // debug value
//}


// void loop() {
//   // Read and convert the potentiometer value
//   int potVal = analogRead(potPin);             // 0 to 1023
//   float voltage = potVal * (5.0 / 1023.0);     // convert to 0 - 5V range

//   // Print out the voltage (for debugging)
//   Serial.print("Voltage: ");
//   Serial.println(voltage);

//   // Compare against 2.5 V to decide rotation direction
//   if (voltage > 2.5) {
//     // Move the motor to the right (clockwise)
//     // Setting a positive speed
//     myStepper.setSpeed(200);   // steps/sec
//   } else {
//     // Move the motor to the left (counterclockwise)
//     // Setting a negative speed
//     myStepper.setSpeed(-200);  // steps/sec
//   }

//   // Run the motor continuously at the set speed
//   // runSpeed() does not use acceleration; it tries to maintain the set speed
//   myStepper.runSpeed();
// }