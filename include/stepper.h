
#include <Arduino.h>

void processCommand(String command);

void moveForward(int steps);
void moveBackward(int steps);
void stopMovement();    
void updatePosition();
void serialEvent();
void clearQueue();
void processQueue();
void executeCommand(String command);


                                      