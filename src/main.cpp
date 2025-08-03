#include <Arduino.h>
#include <queue>

#include <CheapStepper.h>
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


// Stepper motor setup - pins 8,9,10,11 to IN1,IN2,IN3,IN4 on ULN2003 board
CheapStepper stepper(8, 9, 10, 11);

// Global variables
long currentPosition = 0;  // Track absolute position
String inputString = "";   // String to hold incoming serial data
bool stringComplete = false; // Flag for complete serial command
bool motorIsBusy = false; // Flag to indicate if motor is currently movin
std::queue<String> moveQueue; // Queue for move commands

int cbChannelSteps = 30; // Number of steps per channel (adjust as needed)

// Channel to position mapping for 80 channels
// This maps channels 1-80 to their respective positions
// base is zero, so channel 1 is position 0, channel 80 is position 79
std::array<int, 80> cbChannelToPosition = {
  41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
  51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
  61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
  71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
  1,2,3,4,5,6,7,8,9,10,
  11,12,13,14,15,16,17,18,19,20,
  21,22,23,24,25,26,27,28,29,30,
  31,32,33,34,35,36,37,38,39, 40
};

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
  Serial.println("Commands: F<steps>, B<steps>, S (stop), P (position), RPM<value>, Q (queue status), CH<channel>");
  Serial.println("Example: F100 (forward 100 steps), B50 (backward 50 steps), CH41 (go to channel 41)");
}


void loop() {
  // Keep stepper moving if there's an active move
  motorIsBusy = stepper.getStepsLeft() > 0; // Check if motor is busy

  stepper.run();

  // Handle serial input
  serialEvent();

  // Process complete commands
  if (stringComplete) {
    processCommand(inputString);
    stringComplete = false;
  }

  // Process queued commands when motor is idle
  processQueue();
  
  // Update position tracking
  updatePosition();
}

// Function to process serial commands
void processCommand(String command) {
  command.trim(); // Remove whitespace
  command.toUpperCase(); // Convert to uppercase

  inputString = "";
  stringComplete = false;
  
  // If motor is busy and this is a movement command, queue it
  if (motorIsBusy && (command.startsWith("F") || command.startsWith("B") || command.startsWith("CH"))) {
    moveQueue.push(command);
    Serial.println("Befehl in Warteschlange eingereiht: " + command);
    return;
  }
  
  // Execute command immediately
  executeCommand(command);
}

// Function to execute a command
void executeCommand(String command) {
  if (command.startsWith("F")) {
    // Forward movement
    int steps = command.substring(1).toInt();
    if (steps > 0) {
      moveForward(steps);
      Serial.print("Fahre  ");
      Serial.print(steps);
      Serial.println(" Schritte vorwärts");
    }
  }
  else if (command.startsWith("B")) {
    // Backward movement
    int steps = command.substring(1).toInt();
    if (steps > 0) {
      moveBackward(steps);
      Serial.print("Fahre ");
      Serial.print(steps);
      Serial.println(" Schritte rückwärts");
    }
  }
  else if (command == "S") {
    // Stop movement - also clear the queue
    stopMovement();
    clearQueue();
    Serial.println("Motor angehalten - Warteschlange geleert");
  }
  else if (command == "P") {
    // Get position
    Serial.print("Aktuelle Position: ");
    Serial.println(currentPosition);
  }
  else if (command == "Q") {
    // Get queue status
    Serial.print("Warteschlange: ");
    Serial.print(moveQueue.size());
    Serial.println(" Befehle wartend");
    Serial.print("Motor Status: ");
    Serial.println(motorIsBusy ? "Beschäftigt" : "Bereit");
  }
  else if (command.startsWith("RPM")) {
    // Set RPM
    int rpm = command.substring(3).toInt();
    if (rpm > 5 && rpm <= 25) {
      stepper.setRpm(rpm);
      Serial.print("Drehzahl gesetzt auf: ");
      Serial.println(rpm);
    } else {
      Serial.println("Ungültige Drehzahl(6-24)");
    }
  }
  else if (command.startsWith("CH")) {
    // Direct channel command - CH<channel_number>
    int channel = command.substring(2).toInt();
    if (channel >= 1 && channel <= 80) {
      // Calculate position for this channel using the mapping
      int targetPosition = cbChannelToPosition[channel - 1] * cbChannelSteps;
      int stepsToMove = targetPosition - currentPosition;
      
      if (stepsToMove != 0) {
        if (stepsToMove > 0) {
          moveForward(abs(stepsToMove));
          Serial.print("Fahre zu Kanal ");
          Serial.print(channel);
          Serial.print(" - ");
          Serial.print(abs(stepsToMove));
          Serial.println(" Schritte vorwärts");
        } else {
          moveBackward(abs(stepsToMove));
          Serial.print("Fahre zu Kanal ");
          Serial.print(channel);
          Serial.print(" - ");
          Serial.print(abs(stepsToMove));
          Serial.println(" Schritte rückwärts");
        }
      } else {
        Serial.print("Bereits auf Kanal ");
        Serial.println(channel);
      }
    } else {
      Serial.println("Ungültiger Kanal (1-80)");
    }
  }
  else {
    Serial.print("Unbekannter Befehl: ");
    Serial.println(command);
  }
}

// Function to process queued commands
void processQueue() {
  // Only process queue if motor is not busy and there are commands waiting
  if (!motorIsBusy && !moveQueue.empty()) {
    String nextCommand = moveQueue.front();
    moveQueue.pop();
    Serial.println("Führe Befehl aus Warteschlange aus: " + nextCommand);
    executeCommand(nextCommand);
  }
}

// Function to clear the command queue
void clearQueue() {
  while (!moveQueue.empty()) {
    moveQueue.pop();
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
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }

}