import tcp_handler
import threading
import keyboard
import time


def keyboard_controller(server: tcp_handler.TCPServer):
    global data
    ters = -1

    while not stop_event.is_set():
        ser_data = ""
        ser_x = 0
        ser_y = 0

        if keyboard.is_pressed("x"):
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

        ser_data = f"{ser_x}|{ser_y}\n"
        server.send_data(ser_data)
        print(ser_data)

        if data != None:
            if int(data.strip().split("|")[0]) >= 167 or int(data.strip().split("|")[0]) <= 15:
                print("Drone Donmeli")

        time.sleep(0.05)

def response_reader(server: tcp_handler.TCPServer):
    global data

    while not stop_event.is_set():
        data = server.get_data()
        print(data)


data = ""
stop_event = threading.Event()

server = tcp_handler.TCPServer("0.0.0.0", 9998)

threading.Thread(target=response_reader, args=(server, ), daemon=True).start()
threading.Thread(target=keyboard_controller, args=(server, ), daemon=True).start()

try:
    timer = time.time()
    while not stop_event.is_set():
        if time.time() - timer >= 5:
            print("Haberleşiliyor...")
            timer = time.time()

except KeyboardInterrupt:
    print("Çıkılıyor")

finally:
    if not stop_event.is_set():
        stop_event.set()
