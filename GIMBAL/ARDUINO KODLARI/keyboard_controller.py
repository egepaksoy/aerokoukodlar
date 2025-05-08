import serial
import time
import keyboard  # pip install keyboard

# Arduino seri portunu buraya yaz (örnek: "COM3" veya "/dev/ttyUSB0")
ser = serial.Serial("COM5", 9600)
time.sleep(2)  # Arduino'nun başlaması için bekle

print("wasd yada yon tuslari ile kontrol basladi")
ters = input("ters ise -1 duz ise 1 yazın:")
ters = int(ters)

while True:
    ser_data = ""
    ser_x = 0
    ser_y = 0

    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line != "":
                print("Gelen veri:", line)

        if keyboard.is_pressed("c"):
            ser_x = 2
            ser_y = 2
        else:
            if keyboard.is_pressed('right') or keyboard.is_pressed('d'):
                ser_x = -1 * ters

            if keyboard.is_pressed('left') or keyboard.is_pressed('a'):
                ser_x = 1 * ters

            if keyboard.is_pressed('up') or keyboard.is_pressed('w'):
                ser_y = 1 * ters

            if keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                ser_y = -1 * ters

        ser.write(f"{ser_x},{ser_y}\n".encode())
        time.sleep(0.05)

    except KeyboardInterrupt:
        print("Program durduruldu.")
        break
