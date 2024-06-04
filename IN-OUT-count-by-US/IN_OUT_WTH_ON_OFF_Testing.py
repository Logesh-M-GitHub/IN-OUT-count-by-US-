from machine import Pin, time_pulse_us
import utime

# Constants
TRIGGER_PIN_A = 2  # Ultrasonic Sensor A (Entry)
ECHO_PIN_A = 3
TRIGGER_PIN_B = 8  # Ultrasonic Sensor B (Exit)
ECHO_PIN_B = 9
MAX_CAPACITY = 5
DISABLE_TIME = 3  # Time in seconds to disable the other sensor
MIN_DELAY = 0.5   # Minimum delay to prevent multiple counts

# Initialize pins for sensor A (Entry)
trigger_a = Pin(TRIGGER_PIN_A, Pin.OUT)
echo_a = Pin(ECHO_PIN_A, Pin.IN)

# Initialize pins for sensor B (Exit)
trigger_b = Pin(TRIGGER_PIN_B, Pin.OUT)
echo_b = Pin(ECHO_PIN_B, Pin.IN)

BUZZER_PIN = Pin(5, Pin.OUT)

# Variables to keep track of counts
in_count = 0
out_count = 0

# Flags to disable sensors temporarily
sensor_a_enabled = True
sensor_b_enabled = True

# Timestamps for delays
last_entry_time = 0
last_exit_time = 0

# Function to sound the buzzer for 0.5 seconds
def sound_buzzer():
    BUZZER_PIN.on()
    utime.sleep(0.5)
    BUZZER_PIN.off()

# Function to sound the buzzer for 3 seconds
def sound_buzzer_3_seconds():
    BUZZER_PIN.on()
    utime.sleep(3)
    BUZZER_PIN.off()

# Function to measure distance using the ultrasonic sensor
def measure_distance(trigger, echo):
    # Send a 10us pulse to trigger
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()

    # Measure the echo pulse duration
    duration = time_pulse_us(echo, 1, 30000)  # Timeout after 30ms
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
    check_capacity_and_display()
    sensor_b_enabled = False
    last_entry_time = utime.time()

# Function to handle a student exiting the bus
def student_exited():
    global out_count, sensor_a_enabled, last_exit_time
    if in_count > out_count:  # Prevent out_count from exceeding in_count
        out_count += 1
        sound_buzzer()
        check_capacity_and_display()
        sensor_a_enabled = False
        last_exit_time = utime.time()
    else:
        print("No students left to exit")

# Function to check capacity and display the current counts
def check_capacity_and_display():
    current_students = in_count - out_count
    print(f"Students entered: {in_count}")
    print(f"Students exited: {out_count}")
    print(f"Total students in bus: {current_students}")
    if current_students > MAX_CAPACITY:
        exceeding_students = current_students - MAX_CAPACITY
        print(f"***ALERT*** : {exceeding_students} students over capacity.........!")
        print(f"Exceeding students: {exceeding_students}")
    else:
        print(f"Exceeding students: 0")

# Main function to run the student counting system
def main():
    global sensor_a_enabled, sensor_b_enabled, last_entry_time, last_exit_time
    print("Starting student counting system...")
    while True:
        current_time = utime.time()
        
        # Re-enable sensors after disable time
        if not sensor_a_enabled and current_time - last_exit_time >= DISABLE_TIME:
            sensor_a_enabled = True
        if not sensor_b_enabled and current_time - last_entry_time >= DISABLE_TIME:
            sensor_b_enabled = True

        # Measure distance for entry sensor if enabled
        if sensor_a_enabled and current_time - last_entry_time >= MIN_DELAY:
            distance_a = measure_distance(trigger_a, echo_a)
            if distance_a is not None and distance_a < 10:  # Assume a threshold distance for detecting a student
                student_entered()

        # Measure distance for exit sensor if enabled
        if sensor_b_enabled and current_time - last_exit_time >= MIN_DELAY:
            distance_b = measure_distance(trigger_b, echo_b)
            if distance_b is not None and distance_b < 10:  # Assume a threshold distance for detecting a student
                student_exited()

if __name__ == "__main__":
    main()
