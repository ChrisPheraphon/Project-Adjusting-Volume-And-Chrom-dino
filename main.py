from machine import Pin, Timer, SoftI2C, ADC, PWM
from time import sleep
import ssd1306
import random

# Initialize I2C for OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize Button with Pull-Up resistor (active low)
button = Pin(14, Pin.IN, Pin.PULL_UP)
button_jump = Pin(27, Pin.IN, Pin.PULL_UP)  # Button for jump in the game

# Setup LED on Pin 2 (on-board LED for ESP32)
led = PWM(Pin(2), freq=1000)  # PWM frequency at 1kHz

# Setup Speaker on Pin 25 (on-board speaker for ESP32)
speaker = PWM(Pin(25), freq=1000)  # Initial PWM frequency for Speaker

# Potentiometer for Volume Control
potentiometer = ADC(Pin(34))  # Assuming Pin 34 is used for Potentiometer
potentiometer.width(ADC.WIDTH_10BIT)  # 10-bit resolution (0-1023)
potentiometer.atten(ADC.ATTN_11DB)  # Full range (0 - 3.3V)

# Global variables
current_mode = 0  # Start in Mode Selection (Mode 0)
button_press_count = 0  # Counter for button presses
is_holding_button = False  # Track if button is being held
game_over = False  # Track game over status
jump = False  # Track if the player is jumping
double_jump = False  # Track if the player is double-jumping
player_y = 56  # Player's initial Y position
obstacle_x = 128  # Initial X position of the obstacle
speed = 2  # Speed of obstacle
score = 0  # Game score

# Timer for button hold check
hold_timer = Timer(0)  # Assign Timer 0

# Display mode on OLED
def display_mode(mode):
    oled.fill(0)  # Clear screen
    if mode == 0:
        oled.text("Mode Selection", 0, 0)
        oled.text("1: Volume Control", 0, 20)
        oled.text("2: Game Mode", 0, 40)
    elif mode == 1:
        oled.text("Mode 1: Volume", 0, 0)
        oled.text("Adjusting Volume...", 0, 20)
    elif mode == 2:
        if game_over:
            oled.text("Game Over!", 30, 30)
            oled.text("Press Jump to Restart", 0, 50)
        else:
            oled.text("Mode 2: Game", 0, 0)
            oled.text("Score: {}".format(score), 0, 20)
    oled.show()

# Test the speaker
def test_speaker():
    speaker.freq(1000)
    speaker.duty(512)  # 50% duty cycle
    sleep(1)
    speaker.duty(0)

# Adjust volume using Potentiometer
def adjusting_volume():
    pot_value = potentiometer.read()
    volume_percentage = int(pot_value / 1023 * 100)
    
    oled.fill(0)
    oled.text("Mode 1: Volume", 0, 0)
    oled.text("Volume: {}%".format(volume_percentage), 0, 20)
    oled.show()

    led.duty(int(volume_percentage * 1023 / 100))
    speaker.duty(int(volume_percentage * 1023 / 100))
    speaker.freq(200 + int(volume_percentage * 5))

# Handle button interrupt for mode change
def handle_button_interrupt(pin):
    global current_mode, button_press_count
    sleep(0.2)  # Debounce delay (200 ms)
    if pin.value() == 0:  # If the button is still pressed (active low)
        button_press_count += 1  # Increment button press count
        
        if button_press_count == 1:
            current_mode = 1  # Go to Mode 1 (Volume Control)
        elif button_press_count == 2:
            current_mode = 2  # Go to Mode 2 (Game Mode)
        elif button_press_count >= 3:
            current_mode = 2  # Stay in Mode 2 after the 3rd press and onward
        
        display_mode(current_mode)

# Reset to Mode 0 after button held for 5 seconds
def reset_to_mode_0(t):
    global current_mode, button_press_count, is_holding_button, game_over, score
    current_mode = 0  # Reset to Mode 0
    button_press_count = 0  # Reset button press count
    is_holding_button = False  # Stop holding button
    game_over = False  # Reset game status
    score = 0  # Reset score
    display_mode(current_mode)

# Attach interrupt to the button
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_button_interrupt)

# Jump function
def handle_jump(pin):
    global jump, double_jump, game_over
    if game_over:
        reset_game()  # If game over, restart the game
    elif player_y == 56:
        jump = True  # Start jumping
    elif not double_jump:
        double_jump = True  # Perform double jump

# Attach interrupt to the jump button
button_jump.irq(trigger=Pin.IRQ_FALLING, handler=handle_jump)

# Reset the game state
def reset_game():
    global player_y, obstacle_x, score, speed, jump, double_jump, game_over
    player_y = 56
    obstacle_x = 128
    score = 0
    speed = 2
    jump = False
    double_jump = False
    game_over = False

# Update game state (Chrome Dino Style)
def update_game():
    global player_y, obstacle_x, speed, score, jump, double_jump, game_over

    oled.fill(0)  # Clear screen

    # Draw the player (Dino)
    oled.fill_rect(10, player_y, 8, 8, 1)  # Dino is 8x8 square

    # Draw the obstacle
    oled.fill_rect(int(obstacle_x), 56, 8, 8, 1)  # Obstacle is 8x8 square

    # Move the obstacle
    obstacle_x -= speed
    if obstacle_x < 0:
        obstacle_x = 128
        score += 1  # Increase score when obstacle is passed
        speed += 0.1  # Increase speed for more challenge

    # Check for collision
    if obstacle_x < 18 and player_y >= 56:  # Collision detection
        game_over = True
        display_mode(current_mode)
        return

    # Handle jump
    if jump:
        player_y -= 5  # Jump up
        if player_y <= 26:  # Max jump height
            jump = False
    elif double_jump:
        player_y -= 5
        if player_y <= 26:
            double_jump = False
    else:
        if player_y < 56:  # If player is in air, fall down
            player_y += 5

    oled.text("Score: {}".format(score), 0, 0)  # Display score
    oled.show()

# Main program loop
display_mode(current_mode)  # Display the initial mode selection screen
test_speaker()

while True:
    if current_mode == 1:
        adjusting_volume()  # Adjust volume in Mode 1
    elif current_mode == 2:
        if not game_over:
            update_game()  # Update game state if game is not over
    
    if button.value() == 0:  # If the button is pressed
        if not is_holding_button:
            is_holding_button = True  # Track that the button is being held
            hold_timer.init(period=5000, mode=Timer.ONE_SHOT, callback=reset_to_mode_0)
    else:
        is_holding_button = False  # Stop tracking if the button is not pressed
        hold_timer.deinit()  # Stop the timer if the button is released before 5 seconds
    
    sleep(0.1)  # Small delay for stability
