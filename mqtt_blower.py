if(1):
    import RPi.GPIO as GPIO
    import time
    import threading
    import paho.mqtt.client as mqtt

    # GPIO Definitions
    RELAY_FWD = 7     # GPIO7 - Forward Relay
    RELAY_REV = 11    # GPIO11 - Reverse Relay
    SENSOR_1 = 4      # GPIO4 - Position Sensor 1 (Forward End)
    SENSOR_2 = 17     # GPIO17 - Position Sensor 2 (Backward End)
    PUMP = 8

    # MQTT Definitions
    broker_ip = "test.mosquitto.org"
    port = 1883
    topic = "PTS/blower"

    # Global control flags
    pump_active = False
    pump_thread = None

    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_FWD, GPIO.OUT)
    GPIO.setup(RELAY_REV, GPIO.OUT)
    GPIO.setup(PUMP, GPIO.OUT)
    GPIO.setup(SENSOR_1, GPIO.IN)
    GPIO.setup(SENSOR_2, GPIO.IN)

    # Ensure all outputs are off initially
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.LOW)
    GPIO.output(PUMP, GPIO.LOW)

def stop_motor():
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.LOW)
    print("Motor stopped")

def move_left():
    GPIO.output(RELAY_FWD, GPIO.HIGH)
    GPIO.output(RELAY_REV, GPIO.LOW)
    print("Moving Forward...")

def move_right():
    GPIO.output(RELAY_FWD, GPIO.LOW)
    GPIO.output(RELAY_REV, GPIO.HIGH)
    print("Moving Backward...")

def onPump():
    global pump_active
    pump_active = True
    GPIO.output(PUMP, GPIO.HIGH)
    print("Pump Activated")
    for _ in range(100):  # 100 * 0.1s = 10 seconds
        if not pump_active:
            break
        time.sleep(0.1)
    GPIO.output(PUMP, GPIO.LOW)
    pump_active = False
    print("Pump Deactivated")

def start_pump_thread():
    global pump_thread
    pump_thread = threading.Thread(target=onPump)
    pump_thread.start()

def process_command(command):
    global pump_active
    count = 0

    if command == "s":
        print("MQTT Command: FORWARD")
        SensorDetected = False
        while not SensorDetected:
            count += 1
            P1 = GPIO.input(SENSOR_1)
            print(f"Looking For Sensor P1: {P1} | Count: {count}")
            if P1 == 0:
                SensorDetected = True
            elif count < 100:
                move_left()
            else:
                if count > 120:
                    count = 0
                stop_motor()
        stop_motor()
        start_pump_thread()

    elif command == "b":
        print("MQTT Command: BACKWARD")
        SensorDetected = False
        while not SensorDetected:
            count += 1
            P2 = GPIO.input(SENSOR_2)
            print(f"Looking For Sensor P2: {P2} | Count: {count}")
            if P2 == 0:
                SensorDetected = True
            elif count < 100:
                move_right()
            else:
                if count > 120:
                    count = 0
                stop_motor()
        stop_motor()
        start_pump_thread()

    elif command == "stop":
        print("MQTT Command: STOP")
        stop_motor()
        pump_active = False  # This will stop the pump even mid-cycle
        GPIO.output(PUMP, GPIO.LOW)

    else:
        print("Unknown command:", command)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message: {payload}")
    process_command(payload)

# MQTT Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker_ip, port, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    pump_active = False
    stop_motor()
    GPIO.output(PUMP, GPIO.LOW)
    GPIO.cleanup()
