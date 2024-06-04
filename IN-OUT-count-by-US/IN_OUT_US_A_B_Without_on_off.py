from machine import Pin, time_pulse_us
import utime

# Constants
TRIGGER_PIN_A = 2  # Ultrasonic Sensor A (Entry)
ECHO_PIN_A = 3
TRIGGER_PIN_B = 8  # Ultrasonic Sensor B (Exit)
ECHO_PIN_B = 9
MAX_CAPACITY = 5

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
    global in_count
    in_count += 1
    sound_buzzer()
    check_capacity_and_display()

# Function to handle a student exiting the bus
def student_exited():
    global out_count
    out_count += 1
    sound_buzzer()
    check_capacity_and_display()

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
    print("Starting student counting system...")
    while True:
        # Measure distance for entry sensor
        distance_a = measure_distance(trigger_a, echo_a)
        if distance_a is not None and distance_a < 10:  # Assume a threshold distance for detecting a student
            student_entered()
            utime.sleep(2)  # Delay to prevent multiple counts for the same student
        
        # Measure distance for exit sensor
        distance_b = measure_distance(trigger_b, echo_b)
        if distance_b is not None and distance_b < 10:  # Assume a threshold distance for detecting a student
            student_exited()
            utime.sleep(2)  # Delay to prevent multiple counts for the same student

if __name__ == "__main__":
    main()
