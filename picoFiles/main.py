from machine import Pin
import time

# Define the motor control pin
motor_pin = Pin(16, Pin.OUT)  # Adjust the GPIO pin number as per your setup

def control_motor(state):
    """
    Control the motor state.
    :param state: 'ON' to turn on, 'OFF' to turn off
    """
    if state == 'ON':
        motor_pin.on()
        print("Motor turned ON.")
    elif state == 'OFF':
        motor_pin.off()
        print("Motor turned OFF.")
    else:
        print("Invalid state. Use 'ON' or 'OFF'.")

# Serial communication setup
print("Listening for serial commands...")

while True:
    try:
        command = input().strip().upper()  # Read serial input and normalize to uppercase
        if command == "ON":
            control_motor('ON')
        elif command == "OFF":
            control_motor('OFF')
        else:
            print("Unknown command. Use 'ON' or 'OFF'.")
    except Exception as e:
        print("Error:", e)