#include <Arduino.h>

#include <AccelStepper.h>

#include <header.h>

// AFMotor_ConstantSpeed.pde
// -*- mode: C++ -*-
//
// Shows how to use AccelStepper to control a 3-phase motor, such as a HDD spindle motor
// using the Adafruit Motor Shield
// http://www.ladyada.net/make/mshield/index.html.
// Create a subclass of AccelStepper which controls the motor  pins via the
// Motor Shield serial-to-parallel interface



// Arduino pin names for interface to 74HCT595 latch
// on Adafruit Motor Shield
#define MOTORLATCH   12
#define MOTORCLK     4
#define MOTORENABLE  7
#define MOTORDATA    8

// PWM pins, also used to enable motor outputs
#define PWM0A        5
#define PWM0B        6
#define PWM1A        9
#define PWM1B        10
#define PWM2A        11
#define PWM2B        3


// The main purpose of this class is to override setOutputPins to work with Adafruit Motor Shield
class AFMotorShield : public AccelStepper
{
  public:
  AFMotorShield(uint8_t interface = AccelStepper::FULL4WIRE, uint8_t pin1 = 2, uint8_t pin2 = 3, uint8_t pin3 = 4, uint8_t pin4 = 5); 

  virtual void   setOutputPins(uint8_t mask);
};


AFMotorShield::AFMotorShield(uint8_t interface, uint8_t pin1, uint8_t pin2, uint8_t pin3, uint8_t pin4)
    : AccelStepper(interface, pin1, pin2, pin3, pin4) 
{
    // Enable motor control serial to parallel latch
    pinMode(MOTORLATCH, OUTPUT);
    pinMode(MOTORENABLE, OUTPUT);
    pinMode(MOTORDATA, OUTPUT);
    pinMode(MOTORCLK, OUTPUT);
    digitalWrite(MOTORENABLE, LOW);
    
    // enable both H bridges on motor 1
    pinMode(PWM2A, OUTPUT);
    pinMode(PWM2B, OUTPUT);
    pinMode(PWM0A, OUTPUT);
    pinMode(PWM0B, OUTPUT);
    digitalWrite(PWM2A, HIGH);
    digitalWrite(PWM2B, HIGH);
    digitalWrite(PWM0A, HIGH);
    digitalWrite(PWM0B, HIGH);

    setOutputPins(0); // Reset
}
    
// Use the AF Motor Shield serial-to-parallel to set the state of the motor pins
// Caution: the mapping of AccelStepper pins to AF motor outputs is not
// obvious:
// AccelStepper     Motor Shield output
// pin1                M4A
// pin2                M1A
// pin3                M2A
// pin4                M3A
// Caution this is pretty slow and limits the max speed of the motor to about 500/3 rpm
void AFMotorShield::setOutputPins(uint8_t mask)
{
  uint8_t i;
  
  digitalWrite(MOTORLATCH, LOW);
  digitalWrite(MOTORDATA, LOW);

  for (i=0; i<8; i++) 
  {
    digitalWrite(MOTORCLK, LOW);

    if (mask & _BV(7-i))
      digitalWrite(MOTORDATA, HIGH);
    else
      digitalWrite(MOTORDATA, LOW);
 
    digitalWrite(MOTORCLK, HIGH);
  }
  digitalWrite(MOTORLATCH, HIGH);
}

AFMotorShield stepper(AccelStepper::HALF3WIRE, 0, 0, 0, 0); // 3 phase HDD spindle drive

bool motorRunning = false;
String inputString = "";
bool stringComplete = false;


void setup()
{  
   Serial.begin(9600);
   stepper.setMaxSpeed(500);	// divide by 3 to get rpm
   stepper.setAcceleration(80);
   
   Serial.println("Stepper Motor Controller Ready");
   Serial.println("Commands: START, STOP, SPEED:<value>, MOVE:<steps>");
}

void loop()
{  
   // Check for serial commands
   if (stringComplete) {
     processCommand(inputString);
     inputString = "";
     stringComplete = false;
   }
   
   // Run the stepper if it's enabled
   if (motorRunning) {
     stepper.run();
   }
}


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

void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  
  if (command == "START") {
    motorRunning = true;
    stepper.moveTo(10000000);  // Move to a large position
    Serial.println("Motor started");
  }
  else if (command == "STOP") {
    motorRunning = false;
    stepper.stop();
    Serial.println("Motor stopped");
  }
  else if (command.startsWith("SPEED:")) {
    int speed = command.substring(6).toInt();
    if (speed > 0 && speed <= 1000) {
      stepper.setMaxSpeed(speed);
      Serial.println("Speed set to: " + String(speed));
    } else {
      Serial.println("Invalid speed. Use 1-1000");
    }
  }
  else if (command.startsWith("MOVE:")) {
    long steps = command.substring(5).toInt();
    stepper.moveTo(stepper.currentPosition() + steps);
    motorRunning = true;
    Serial.println("Moving " + String(steps) + " steps");
  }
  else {
    Serial.println("Unknown command: " + command);
  }
}
