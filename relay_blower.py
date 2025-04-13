import RPi.GPIO as GPIO
import time

# Define GPIO pins
RELAY_FWD = 7     # GPIO7 - Forward Relay
RELAY_REV = 11    # GPIO11 - Reverse Relay
SENSOR_1 = 4      # GPIO4 - Position Sensor 1 (Forward End)
SENSOR_2 = 17     # GPIO17 - Position Sensor 2 (Backward End)

PUMP = 8
count=0
# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_FWD, GPIO.OUT)
GPIO.setup(RELAY_REV, GPIO.OUT)
GPIO.setup(PUMP, GPIO.OUT)
GPIO.setup(SENSOR_1, GPIO.IN)
GPIO.setup(SENSOR_2, GPIO.IN)

# Make sure relays are off at start
GPIO.output(RELAY_FWD, GPIO.LOW)
GPIO.output(RELAY_REV, GPIO.LOW)
GPIO.output(PUMP, GPIO.LOW)

def read_sensors():
    """Reads and returns the states of P1 and P2"""
    P1 = GPIO.input(4)
    P2 = GPIO.input(17)
    return f"P1: {P1} | P2: {P2}"
    
def stop_motor():
    #GPIO.output(RELAY_FWD, GPIO.HIGH)
    #GPIO.output(RELAY_REV, GPIO.HIGH)
    #time.sleep(0.5)
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.LOW)
    print("Motor stopped")

def move_forward():
    GPIO.output(RELAY_FWD, GPIO.HIGH)
    GPIO.output(RELAY_REV, GPIO.LOW)
    
    print("Moving Forward...")
    
def move_forward_slow():
    GPIO.output(RELAY_FWD, GPIO.HIGH)
    GPIO.output(RELAY_REV, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.LOW)
    time.sleep(0.1)
    print("Moving Forward...")

def onPump():
    GPIO.output(PUMP, GPIO.HIGH)
    time.sleep(10)
    GPIO.output(PUMP, GPIO.LOW)

def move_backward():
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.HIGH)
    print("Moving Backward...")
    
def move_backward_slow():
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.LOW)
    time.sleep(0.1)
    
    

try:
    direction = input("Enter direction (f = forward / b = backward): ")

    if direction == 'f':
        SensorDetected = False
        count=0
        while not SensorDetected:
            count+=1
            P1 = GPIO.input(SENSOR_1)
            print("Looking For Sensor P1:",P1)
            print(count)
            if P1 == 0:
                SensorDetected=True
            if count<100:
                print("Forward")
                move_forward()
            else:
                if count>120:
                    count=0
                print("Stop")
                stop_motor()
        print("Sensor Detected .. Stopping Motor")
        stop_motor()
        onPump()
        
    elif direction == 'b':
        SensorDetected = False
        count=0
        while not SensorDetected:
            count+=1
            P2 = GPIO.input(SENSOR_2)
            print("Looking For Sensor P1:",P2)
            print(count)
            if P2 == 0:
                SensorDetected=True
            if count<100:
                print("Forward")
                move_backward()
            else:
                if count>120:
                    count=0
                print("Stop")
                stop_motor()
        print("Sensor Detected .. Stopping Motor")
        stop_motor()
        onPump()
    else:
        print("Invalid input. Enter 'f' or 'b'.")
        stop_motor()

except KeyboardInterrupt:
    print("Stopped by user")
    stop_motor()
    count=0

finally:
    count=0
    stop_motor()
    GPIO.cleanup()
