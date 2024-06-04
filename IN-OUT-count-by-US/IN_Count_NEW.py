from machine import Pin, time_pulse_us
import utime

# Constants
TRIGGER_PIN = 2
ECHO_PIN = 3
MAX_CAPACITY = 5

# Initialize pins
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
led = Pin(25, Pin.OUT)  # Using onboard LED for alert (or connect an external LED/buzzer)

# Variables to keep track of counts
in_count = 0
exceeding_students = 0


def sound_buzzer(): 
    BUZZER_PIN.on()
    utime.sleep(1)
    BUZZER_PIN.off()


def measure_distance():
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



def student_entered():
    global in_count, exceeding_students
    in_count += 1
    if in_count > MAX_CAPACITY:
        exceeding_students = in_count - MAX_CAPACITY
        alert_excess_students(exceeding_students)
    else:
        exceeding_students = 0
    display_counts()



def alert_excess_students(excess):
    print(f"Alert: {excess} students over capacity!")
    led.high()  # Turn on LED for alert
    utime.sleep(2)  # Keep the LED on for 2 seconds
    led.low()  # Turn off LED

def display_counts():
    print(f"Students Entered: {in_count}")
    if exceeding_students > 0:
        print(f"Exceeding students: {exceeding_students}")

def main():
    print("Starting student counting system...")
    while True:
        distance = measure_distance()
        if distance is not None and distance < 50:  # Assume a threshold distance for detecting a student
            student_entered()
            utime.sleep(2)  # Delay to prevent multiple counts for the same student

if __name__ == "__main__":
    main()
