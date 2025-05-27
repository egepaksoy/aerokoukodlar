import tcp_handler
import time

client = tcp_handler.TCPClient("192.168.31.222", 9998)

value = 80
max_angle, min_angle = 170, 10

try:
    timer = time.time()
    while True:
        data = client.get_data()

        if data != None:
            print(data)
            value += int(data.strip().split("|")[0]) * 5

        client.send_data(f"{value}|0\n")
        timer = time.time()

except KeyboardInterrupt:
    print("Çıkıldı")