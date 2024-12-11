from machine import Pin, SoftI2C, Timer
import ssd1306
from time import sleep
import random

# Setup I2C for OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # ใช้ I2C สำหรับการเชื่อมต่อกับหน้าจอ OLED
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # หน้าจอ OLED ความละเอียด 128x64

# Button setup for jump (ใช้ปุ่มเพื่อกระโดด)
button = Pin(14, Pin.IN, Pin.PULL_UP)  # กำหนดให้ GPIO 14 เป็นปุ่ม และใช้ Pull-up resistor

# Global variables for game
player_y = 56  # ตำแหน่ง Y ของตัวละคร (เริ่มที่ตำแหน่งบนพื้น)
jump = False  # ตัวแปรเพื่อติดตามว่าตัวละครกำลังกระโดดหรือไม่
double_jump = False  # ติดตามว่าตัวละครกระโดดครั้งที่สองได้หรือไม่
jump_height = 30  # ความสูงสูงสุดของการกระโดด
obstacle_x = 128  # ตำแหน่ง X ของสิ่งกีดขวาง (เริ่มต้นนอกจอทางขวา)
speed = 2  # ความเร็วของสิ่งกีดขวาง
score = 0  # คะแนนของเกม
jump_count = 0  # ตัวนับจำนวนการกระโดด (สำหรับ double jump)

# ฟังก์ชันการวาดตัวละคร (Draw player as a square)
def draw_player():
    oled.fill_rect(10, player_y, 8, 8, 1)  # วาดตัวละครที่ตำแหน่ง player_y

# ฟังก์ชันการวาดสิ่งกีดขวาง (Draw obstacle)
def draw_obstacle():
    oled.fill_rect(int(obstacle_x), 56, 8, 8, 1)  # วาดสิ่งกีดขวางที่ตำแหน่ง obstacle_x (ใช้ int เพื่อป้องกัน float)

# ฟังก์ชันอัพเดตสถานะของเกม (Update game state)
def update():
    global player_y, jump, double_jump, obstacle_x, speed, score, jump_count

    oled.fill(0)  # เคลียร์หน้าจอ OLED

    # วาดตัวละครและสิ่งกีดขวาง
    draw_player()
    draw_obstacle()

    # ย้ายสิ่งกีดขวางจากขวาไปซ้าย
    obstacle_x -= speed  # ลดค่าตำแหน่ง X ของสิ่งกีดขวาง
    if obstacle_x < 0:  # หากสิ่งกีดขวางหลุดจากจอทางซ้าย
        obstacle_x = 128  # รีเซ็ตตำแหน่ง X ของสิ่งกีดขวางกลับไปทางขวา
        score += 1  # เพิ่มคะแนนเมื่อหลบสิ่งกีดขวางได้
        speed += 0.1  # เพิ่มความเร็วเพื่อเพิ่มความยากของเกม

    # ตรวจสอบการชนกับสิ่งกีดขวาง (Check collision)
    if obstacle_x < 18 and player_y >= 56:  # ถ้าตำแหน่งของสิ่งกีดขวางชนกับตัวละคร
        oled.text('Game Over', 30, 30)  # แสดงข้อความ "Game Over"
        oled.show()  # แสดงผล
        sleep(2)  # รอ 2 วินาที
        reset_game()  # รีเซ็ตเกม

    # การกระโดดของตัวละคร (Handle jumping)
    if jump:  # ถ้ากำลังกระโดด
        player_y -= 5  # เลื่อนตัวละครขึ้น
        if player_y <= 56 - jump_height:  # ถ้าถึงความสูงสูงสุด
            jump = False  # หยุดการกระโดด
    elif double_jump:  # ตรวจสอบถ้ากระโดดสองครั้ง (double jump)
        player_y -= 5  # เลื่อนตัวละครขึ้น
        if player_y <= 56 - jump_height:  # ถ้าถึงความสูงสูงสุดในการกระโดดครั้งที่สอง
            double_jump = False  # หยุด double jump
    else:
        if player_y < 56:  # ถ้าตัวละครยังไม่อยู่บนพื้น
            player_y += 5  # ตัวละครตกลงพื้น

    # แสดงคะแนน (Display score)
    oled.text("Score: {}".format(score), 0, 0)  # แสดงคะแนนที่มุมซ้ายบน

    oled.show()  # แสดงผลบนหน้าจอ OLED

# ฟังก์ชันรีเซ็ตเกม (Reset game)
def reset_game():
    global obstacle_x, player_y, jump, score, speed, double_jump, jump_count
    obstacle_x = 128  # รีเซ็ตตำแหน่งของสิ่งกีดขวาง
    player_y = 56  # รีเซ็ตตำแหน่งของตัวละคร (อยู่บนพื้น)
    jump = False  # รีเซ็ตการกระโดด
    double_jump = False  # รีเซ็ต double jump
    score = 0  # รีเซ็ตคะแนน
    speed = 2  # รีเซ็ตความเร็ว
    jump_count = 0  # รีเซ็ตจำนวนการกระโดด

# ฟังก์ชันที่ทำงานเมื่อกดปุ่ม (Interrupt for jump and double jump)
def handle_button(pin):
    global jump, double_jump, jump_count
    if player_y == 56:  # ถ้าตัวละครอยู่บนพื้น
        jump = True  # เริ่มการกระโดดครั้งแรก
        jump_count = 1  # ตั้งค่า jump_count เป็น 1
    elif jump_count == 1 and not double_jump:  # ถ้ากระโดดครั้งแรกแล้วและยังไม่ได้กระโดดสองครั้ง
        double_jump = True  # เริ่ม double jump
        jump_count = 2  # ตั้งค่า jump_count เป็น 2

# Attach interrupt to the button (เชื่อมต่อ Interrupt กับปุ่ม)
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_button)  # เรียกฟังก์ชัน handle_button เมื่อกดปุ่ม

# Main game loop
while True:
    update()  # อัพเดตสถานะของเกมในทุกๆ ลูป
    sleep(0.05)  # หน่วงเวลาเล็กน้อยเพื่อให้การแสดงผลนุ่มนวล

