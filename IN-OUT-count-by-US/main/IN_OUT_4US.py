from machine import Pin, time_pulse_us
import utime

# Constants
TRIGGER_PIN_A_LEFT = 2  # Ultrasonic Sensor A Left (Entry)
ECHO_PIN_A_LEFT = 3
TRIGGER_PIN_A_RIGHT = 8 # Ultrasonic Sensor A Right (Entry)
ECHO_PIN_A_RIGHT = 9

TRIGGER_PIN_B_LEFT = 14  # Ultrasonic Sensor B Left (Exit)
ECHO_PIN_B_LEFT = 15
TRIGGER_PIN_B_RIGHT = 0 # Ultrasonic Sensor B Right (Exit)
ECHO_PIN_B_RIGHT = 1

MAX_CAPACITY = 10
DISABLE_TIME = 5  # Time in seconds to disable the other sensor
MIN_DELAY = 1  # Minimum delay to prevent multiple counts

# Initialize pins for sensor A (Entry)
trigger_a_left = Pin(TRIGGER_PIN_A_LEFT, Pin.OUT)
echo_a_left = Pin(ECHO_PIN_A_LEFT, Pin.IN)
trigger_a_right = Pin(TRIGGER_PIN_A_RIGHT, Pin.OUT)
echo_a_right = Pin(ECHO_PIN_A_RIGHT, Pin.IN)

# Initialize pins for sensor B (Exit)
trigger_b_left = Pin(TRIGGER_PIN_B_LEFT, Pin.OUT)
echo_b_left = Pin(ECHO_PIN_B_LEFT, Pin.IN)
trigger_b_right = Pin(TRIGGER_PIN_B_RIGHT, Pin.OUT)
echo_b_right = Pin(ECHO_PIN_B_RIGHT, Pin.IN)

BUZZER_PIN = Pin(5, Pin.OUT)
GREEN_LED_PIN = Pin(6, Pin.OUT)
RED_LED_PIN = Pin(7, Pin.OUT)

# Variables to keep track of counts
in_count = 0
out_count = 0

# Flags to disable sensors temporarily
sensor_a_enabled = True
sensor_b_enabled = True

# Timestamps for delays
last_entry_time = 0
last_exit_time = 0

# Buzzer state variables
buzzer_on = False
buzzer_alert = False
buzzer_end_time = 0

# Function to sound the buzzer for a specified duration
def sound_buzzer(duration=0.5):
    global buzzer_on, buzzer_end_time
    BUZZER_PIN.on()
    buzzer_on = True
    buzzer_end_time = utime.ticks_add(utime.ticks_ms(), int(duration * 1000))

# Function to start a long alert with the buzzer
def start_buzzer_alert(duration=2):
    global buzzer_alert, buzzer_end_time
    BUZZER_PIN.on()
    buzzer_alert = True
    buzzer_end_time = utime.ticks_add(utime.ticks_ms(), int(duration * 1000))

# Function to stop the buzzer
def stop_buzzer():
    global buzzer_on, buzzer_alert
    BUZZER_PIN.off()
    buzzer_on = False
    buzzer_alert = False

# Function to measure distance using the ultrasonic sensor
def measure_distance(trigger, echo):
    # Send a 10us pulse to trigger
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()

    # Measure the echo pulse duration
    duration = time_pulse_us(echo, 1, 30000)  # Timeout after 20ms
    if duration < 0:
        return None  # Timeout, no valid measurement
    
    # Calculate distance in cm (speed of sound is 34300 cm/s)
    distance = (duration * 0.0343) / 2
    return distance

# Function to handle a student entering the bus
def student_entered():
    global in_count, sensor_b_enabled, last_entry_time
    in_count += 1
    sound_buzzer()
    sensor_b_enabled = False
    last_entry_time = utime.time()

# Function to handle a student exiting the bus
def student_exited():
    global out_count, sensor_a_enabled, last_exit_time
    if in_count > out_count:  # Prevent out_count from exceeding in_count
        out_count += 1
        sound_buzzer()
        sensor_a_enabled = False
        last_exit_time = utime.time()
    else:
        print("No students left to exit")
        utime.sleep(1)

# Function to check capacity and display the current counts
def check_capacity_and_display():
    current_students = in_count - out_count
    print(f"Students ENTERED = {in_count}")
    print(f"Students EXITED = {out_count}")
    print(f"TOTAL STUDENTS in bus = {current_students}")
    if current_students > MAX_CAPACITY:
        exceeding_students = current_students - MAX_CAPACITY
        print(f"!!***ALERT***!! = {exceeding_students} students over capacity.........!")
        print(f"EXCEEDING Students = {exceeding_students}")
        start_buzzer_alert()
    else:
        print(f"EXCEEDING students = 0")

# Main function to run the student counting system
def main():
    global sensor_a_enabled, sensor_b_enabled, last_entry_time, last_exit_time, buzzer_on, buzzer_alert, buzzer_end_time
    print("Starting student counting system...")
    while True:
        current_time = utime.time()
        
        # Re-enable sensors after disable time
        if not sensor_a_enabled and current_time - last_exit_time >= DISABLE_TIME:
            sensor_a_enabled = True
        if not sensor_b_enabled and current_time - last_entry_time >= DISABLE_TIME:
            sensor_b_enabled = True

        # Measure distance for entry sensors if enabled
        if sensor_a_enabled and current_time - last_entry_time >= MIN_DELAY:
            distance_a_left = measure_distance(trigger_a_left, echo_a_left)
            distance_a_right = measure_distance(trigger_a_right, echo_a_right)
            if (distance_a_left is not None and distance_a_left < 10) or (distance_a_right is not None and distance_a_right < 10):
                student_entered()
                check_capacity_and_display()  # Moved inside the condition to reduce unnecessary calls

        # Measure distance for exit sensors if enabled
        if sensor_b_enabled and current_time - last_exit_time >= MIN_DELAY:
            distance_b_left = measure_distance(trigger_b_left, echo_b_left)
            distance_b_right = measure_distance(trigger_b_right, echo_b_right)
            if (distance_b_left is not None and distance_b_left < 10) or (distance_b_right is not None and distance_b_right < 10):
                student_exited()
                check_capacity_and_display()  # Moved inside the condition to reduce unnecessary calls

        # Check if the buzzer needs to be turned off
        if buzzer_on and utime.ticks_diff(utime.ticks_ms(), buzzer_end_time) >= 0:
            stop_buzzer()

if __name__ == "__main__":
    main()
