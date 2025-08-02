#include <Arduino.h>

#include <stepper.h>

/*
 * Magnet Loop Antenna Stepper Controller
 * //////////////////////////////////////
 * Controller for 11m Band Magnet Loop Antenna
 * with 80 channels and variable capacitor control
 * 
 * Serial Commands:
 * F<steps>  - Move forward (clockwise) by <steps>
 * B<steps>  - Move backward (counter-clockwise) by <steps>
 * S         - Stop current movement
 * P         - Get current position
 * RPM<value> - Set RPM to <value>
 * 
 * Examples:
 * F1        - Move 1 step forward
 * B10       - Move 10 steps backward
 * F1000     - Move 1000 steps forward
 * //////////////////////////////////////
 */

#include <CheapStepper.h>

// Stepper motor setup - pins 8,9,10,11 to IN1,IN2,IN3,IN4 on ULN2003 board
CheapStepper stepper(8, 9, 10, 11);

// Global variables
long currentPosition = 0;  // Track absolute position
String inputString = "";   // String to hold incoming serial data
bool stringComplete = false; // Flag for complete serial command
bool motorIsBusy = false; // Flag to indicate if motor is currently moving
bool motorBusyMsgSend = false; // Flag to indicate if busy message has been sent


void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set stepper RPM (adjust as needed for your setup)
  stepper.setRpm(8);

  stepper.set4076StepMode(); // Set stepper to 4076 steps per revolution (28BYJ-48)
  
  // Reserve space for input string
  inputString.reserve(200);
  
  // Print startup information
  Serial.println("Magnet Loop Antenna Controller Ready");
  Serial.print("Stepper RPM: ");
  Serial.println(stepper.getRpm());
  Serial.print("Steps per revolution: ");
  Serial.println(4096); // Standard for 28BYJ-48 stepper
  Serial.println("Commands: F<steps>, B<steps>, S (stop), P (position), RPM<value>");
  Serial.println("Example: F100 (forward 100 steps), B50 (backward 50 steps)");
}


void loop() {
  // Keep stepper moving if there's an active move
  motorIsBusy = stepper.getStepsLeft() > 0; // Check if motor is busy
  stepper.run();

  serialEvent();
  if(!motorIsBusy) {
    motorBusyMsgSend = false; // Reset busy message flag when not moving
    // Process serial commands
    if (stringComplete) {
      processCommand(inputString);
      inputString = "";
      stringComplete = false;
    }
  }
  
  // Update position tracking
  updatePosition();
}

// Function to process serial commands
void processCommand(String command) {
  command.trim(); // Remove whitespace
  command.toUpperCase(); // Convert to uppercase
  
  if (command.startsWith("F")) {
    // Forward movement
    int steps = command.substring(1).toInt();
    if (steps > 0) {
      moveForward(steps);
      Serial.print("Moving forward ");
      Serial.print(steps);
      Serial.println(" steps");
    }
  }
  else if (command.startsWith("B")) {
    // Backward movement
    int steps = command.substring(1).toInt();
    if (steps > 0) {
      moveBackward(steps);
      Serial.print("Moving backward ");
      Serial.print(steps);
      Serial.println(" steps");
    }
  }
  else if (command == "S") {
    // Stop movement
    stopMovement();
    Serial.println("Movement stopped");
  }
  else if (command == "P") {
    // Get position
    Serial.print("Position: ");
    Serial.println(currentPosition);
  }
  else if (command.startsWith("RPM")) {
    // Set RPM
    int rpm = command.substring(3).toInt();
    if (rpm > 0 && rpm <= 20) {
      stepper.setRpm(rpm);
      Serial.print("RPM set to: ");
      Serial.println(rpm);
    } else {
      Serial.println("Invalid RPM (1-20)");
    }
  }
  else {
    Serial.println("Unknown command");
  }
}

// Movement functions
void moveForward(int steps) {
  stepper.newMove(true, steps); // true = clockwise
}

void moveBackward(int steps) {
  stepper.newMove(false, steps); // false = counter-clockwise
}

void stopMovement() {
  stepper.stop();
}

// Update position tracking
void updatePosition() {
  static long lastStep = 0;
  long currentStep = stepper.getStep();
  
  if (currentStep != lastStep) {
    currentPosition += (currentStep - lastStep);
    lastStep = currentStep;
  }
}

// Serial event handler
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if(inChar != NULL && motorIsBusy && !motorBusyMsgSend) { 
      // If motor is busy, ignore new commands
      Serial.println("Motor is busy, ignoring new commands");
      motorBusyMsgSend = true; // Set flag to indicate busy message has been sent
      return;
    }
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}