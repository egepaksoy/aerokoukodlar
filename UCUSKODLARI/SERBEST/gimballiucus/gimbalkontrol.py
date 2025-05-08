import serial_handler

joystick = serial_handler.Serial_Control(port="com3")
servo = serial_handler.Serial_Control(port="com15")

def check(val):
    if val != None or val != "":
        if "|" in val:
            if len(val.split("|")) == 2:
                return True
    return False

while True:
    gimbal_val = joystick.read_value()
    if check(gimbal_val):
        gimbal_val = gimbal_val.strip()
        gimbal_val = f"{gimbal_val.split('|')[0]}|{gimbal_val.split("|")[1]}\n"

        servo.send_to_arduino(gimbal_val)
        print(f"joystick val: {gimbal_val}")

        servo_val = servo.read_value()
        print(f"gimbal val: {servo_val}")