#include <Arduino.h>
#include <queue>

#include <CheapStepper.h>
#include <stepper.h>
#include "Arduino_LED_Matrix.h"

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

// LED Matrix setup
ArduinoLEDMatrix matrix;

// Global variables
long currentPosition = 0;  // Track absolute position
String inputString = "";   // String to hold incoming serial data
bool stringComplete = false; // Flag for complete serial command
bool motorIsBusy = false; // Flag to indicate if motor is currently movin
std::queue<String> moveQueue; // Queue for move commands
int currentChannel = 1;   // Track current channel for LED matrix display

// Calibration variables - will be set by controller
int cbChannelSteps = 30; // Number of steps per channel (fallback value)
long channel41Position = 0; // Base position for channel 41 (lowest frequency)
long channel40Position = 2400; // Position for channel 40 (highest frequency)
bool calibrationReceived = false; // Flag to indicate if calibration was received

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

// LED Matrix digit patterns (5x7 pixels for digits 0-9)
// Each digit is represented as 5 bytes, each bit representing a pixel
const byte digitPatterns[10][5] = {
  // 0
  {0b01110, 0b10001, 0b10001, 0b10001, 0b01110},
  // 1  
  {0b00100, 0b01100, 0b00100, 0b00100, 0b01110},
  // 2
  {0b01110, 0b10001, 0b00010, 0b01100, 0b11111},
  // 3
  {0b01110, 0b10001, 0b00110, 0b10001, 0b01110},
  // 4
  {0b10001, 0b10001, 0b11111, 0b00001, 0b00001},
  // 5
  {0b11111, 0b10000, 0b11110, 0b00001, 0b11110},
  // 6
  {0b01110, 0b10000, 0b11110, 0b10001, 0b01110},
  // 7
  {0b11111, 0b00001, 0b00010, 0b00100, 0b01000},
  // 8
  {0b01110, 0b10001, 0b01110, 0b10001, 0b01110},
  // 9
  {0b01110, 0b10001, 0b01111, 0b00001, 0b01110}
};

// Function to display a two-digit number on LED matrix
void displayChannelOnMatrix(int channel) {
  if (channel < 1 || channel > 80) return;
  
  // Clear the frame
  byte frame[8][12] = {0};
  
  // Get tens and units digits
  int tens = channel / 10;
  int units = channel % 10;
  
  // Display tens digit (left side, columns 1-5)
  if (tens > 0) { // Don't display leading zero
    for (int row = 0; row < 5; row++) {
      for (int col = 0; col < 5; col++) {
        if (digitPatterns[tens][row] & (1 << (4-col))) {
          frame[row + 1][col + 1] = 1;
        }
      }
    }
  }
  
  // Display units digit (right side, columns 7-11)
  for (int row = 0; row < 5; row++) {
    for (int col = 0; col < 5; col++) {
      if (digitPatterns[units][row] & (1 << (4-col))) {
        frame[row + 1][col + 7] = 1;
      }
    }
  }
  
  // Render the frame on the matrix
  matrix.renderBitmap(frame, 8, 12);
}

// Function to calculate current channel from position
int calculateChannelFromPosition(long position) {
  if (!calibrationReceived) {
    // Use fallback calculation
    int estimatedChannel = (position / cbChannelSteps) + 1;
    if (estimatedChannel < 1) return 1;
    if (estimatedChannel > 80) return 80;
    return estimatedChannel;
  }
  
  // Use calibrated calculation
  if (position < channel41Position) return 41; // Below range
  if (position > channel40Position) return 40; // Above range
  
  // Calculate frequency position (0-79)
  float stepsPerChannel = (float)(channel40Position - channel41Position) / 79.0;
  int freqPos = (int)((position - channel41Position) / stepsPerChannel + 0.5); // Round to nearest
  
  if (freqPos < 0) freqPos = 0;
  if (freqPos > 79) freqPos = 79;
  
  return cbChannelToPosition[freqPos];
}

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LED matrix
  matrix.begin();
  
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
  Serial.println("Commands: F<steps>, B<steps>, S (stop), P (position), RPM<value>, Q (queue status), CH<channel>, D (display)");
  Serial.println("Calibration: CAL<ch41_pos>,<ch40_pos>, SETPOS<position>");
  Serial.println("Example: F100 (forward 100 steps), B50 (backward 50 steps), CH41 (go to channel 41), D (refresh display)");
  Serial.println("Calibration Example: CAL1000,2500 SETPOS1000");
  Serial.println("LED Matrix shows current channel (01-80)");
  
  // Display initial channel on LED matrix
  displayChannelOnMatrix(currentChannel);
}


void loop() {
  // Keep stepper moving if there's an active move
  bool previouslyBusy = motorIsBusy;
  motorIsBusy = stepper.getStepsLeft() != 0; // Check if motor is busy (can be negative for backward moves)

  // Detect when motor finishes moving
  if (previouslyBusy && !motorIsBusy) {
    Serial.println("Motor fertig - Bewegung abgeschlossen");
    Serial.print("Aktuelle Position: ");
    Serial.println(currentPosition);
  }

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
      Serial.print("Motor startet - Fahre ");
      Serial.print(steps);
      Serial.println(" Schritte vorwärts");
    }
  }
  else if (command.startsWith("B")) {
    // Backward movement
    int steps = command.substring(1).toInt();
    if (steps > 0) {
      moveBackward(steps);
      Serial.print("Motor startet - Fahre ");
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
    currentChannel = calculateChannelFromPosition(currentPosition);
    // Get position
    Serial.print("Aktuelle Position: ");
    Serial.println(currentPosition);
    Serial.print("Aktueller Kanal: ");
    Serial.println(currentChannel);
    // Update LED matrix display
    displayChannelOnMatrix(currentChannel);
  }
  else if (command == "Q") {
    // Get queue status
    Serial.print("Warteschlange: ");
    Serial.print(moveQueue.size());
    Serial.println(" Befehle wartend");
    Serial.print("Motor Status: ");
    Serial.println(motorIsBusy ? "Beschäftigt" : "Bereit");
  }
  else if (command == "D") {
    // Display current channel on LED matrix
    Serial.print("Zeige Kanal auf Matrix: ");
    Serial.println(currentChannel);
    displayChannelOnMatrix(currentChannel);
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
      // Calculate position for this channel using calibration if available
      long targetPosition;
      
      if (calibrationReceived) {
        // Use calibrated calculation
        // Find frequency position of the channel (0-79)
        int freqPos = -1;
        for (int i = 0; i < 80; i++) {
          if (cbChannelToPosition[i] == channel) {
            freqPos = i;
            break;
          }
        }
        
        if (freqPos >= 0) {
          // Calculate position based on calibration
          // Channel 41 is at frequency position 0, Channel 40 is at frequency position 79
          float stepsPerChannel = (float)(channel40Position - channel41Position) / 79.0;
          targetPosition = channel41Position + (long)(freqPos * stepsPerChannel);
        } else {
          Serial.println("Fehler: Kanal nicht in Frequenz-Mapping gefunden");
          return;
        }
      } else {
        // Use fallback calculation
        targetPosition = cbChannelToPosition[channel - 1] * cbChannelSteps;
        Serial.println("Warnung: Verwende Fallback-Berechnung - Kalibrierung fehlt");
      }
      
      int stepsToMove = targetPosition - currentPosition;
      
      // Update current channel and display on LED matrix
      currentChannel = channel;
      displayChannelOnMatrix(currentChannel);
      
      if (stepsToMove != 0) {
        if (stepsToMove > 0) {
          moveForward(abs(stepsToMove));
          Serial.print("Motor startet - Fahre zu Kanal ");
          Serial.print(channel);
          Serial.print(" - ");
          Serial.print(abs(stepsToMove));
          Serial.println(" Schritte vorwärts");
        } else {
          moveBackward(abs(stepsToMove));
          Serial.print("Motor startet - Fahre zu Kanal ");
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
  else if (command.startsWith("CAL")) {
    // Calibration command - CAL<ch41_pos>,<ch40_pos>
    String params = command.substring(3);
    int commaIndex = params.indexOf(',');
    
    if (commaIndex > 0) {
      long ch41Pos = params.substring(0, commaIndex).toInt();
      long ch40Pos = params.substring(commaIndex + 1).toInt();
      
      // Validate calibration values
      if (ch40Pos > ch41Pos && ch41Pos >= 0 && ch40Pos <= 4075) {
        channel41Position = ch41Pos;
        channel40Position = ch40Pos;
        calibrationReceived = true;
        
        // Calculate steps per channel
        float stepsPerChannel = (float)(channel40Position - channel41Position) / 79.0;
        cbChannelSteps = (int)stepsPerChannel; // Update fallback value too
        
        Serial.print("Kalibrierung empfangen: CH41=");
        Serial.print(channel41Position);
        Serial.print(", CH40=");
        Serial.print(channel40Position);
        Serial.print(", Schritte/Kanal=");
        Serial.println(stepsPerChannel);
      } else {
        Serial.println("Ungültige Kalibrierung: CH40 muss > CH41 sein, Bereich 0-4075");
      }
    } else {
      Serial.println("Kalibrierung Format: CAL<ch41_pos>,<ch40_pos>");
    }
  }
  else if (command.startsWith("SETPOS")) {
    // Set current position - SETPOS<position>
    long newPos = command.substring(6).toInt();
    currentPosition = newPos;
    Serial.print("Position gesetzt auf: ");
    Serial.println(currentPosition);
    updatePosition();
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
  static int lastChannel = 1;
  long currentStep = stepper.getStep();
  
  if (currentStep != lastStep) {
    currentPosition += (currentStep - lastStep);
    lastStep = currentStep;
    
    // Update current channel based on position
    int newChannel = calculateChannelFromPosition(currentPosition);
    if (newChannel != lastChannel) {
      currentChannel = newChannel;
      displayChannelOnMatrix(currentChannel);
      lastChannel = newChannel;
    }
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