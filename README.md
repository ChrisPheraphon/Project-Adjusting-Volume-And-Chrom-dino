# Project Adjusting Volume And Chrome Dino

This project integrates a **volume adjustment system** with a **Chrome Dino-style game**. It showcases a combination of hardware controls and gaming logic using Python, MicroPython, and relevant libraries.

---

## Features

- **Volume Adjustment**: Use hardware components (e.g., potentiometer) to adjust sound volume dynamically.
- **Chrome Dino Game**: A simplified version of the famous dinosaur game, playable with button inputs or keyboard controls.
- **OLED Display Support**: Visual feedback on the OLED screen during gameplay and volume adjustment.

---

## Technology Stack

- **Programming Language**: Python, MicroPython
- **Hardware Components**: 
  - Potentiometer
  - Buttons
  - OLED Display (SSD1306)
- **Libraries**:
  - `machine` (MicroPython)
  - `ssd1306` for OLED screen control

---

## File Structure

- `main.py`: The main logic for volume adjustment and game control.
- `dino_game.py`: Contains the game logic for Chrome Dino.
- `ssd1306.py`: Library for controlling the OLED display.

---

## How to Use

1. **Setup the hardware**:
   - Connect the potentiometer, buttons, and OLED display to your microcontroller (e.g., ESP32 or Raspberry Pi Pico).
   
2. **Upload the files**:
   - Use **Thonny** or another MicroPython-compatible IDE to upload the files to your device.

3. **Run the program**:
   - Execute `main.py` to start the system.

4. **Control**:
   - Adjust the volume with the potentiometer.
   - Play the Dino game using the buttons.

---

## Future Enhancements

- Add scoring and high-score tracking to the game.
- Integrate sound effects for better feedback.
- Expand hardware compatibility.

---

## Author

**Chris Pheraphon**  
For inquiries or collaboration, feel free to contact me via GitHub.

---

