import tcpudp_handler
import json
import time

config = json.load(open("config.json", "r"))

server = tcpudp_handler.TCPServer(9999)

server.start()

start_time = time.time()
while True:
    data = server.get_data()
    if data != None:
        print(data)
        server.send_data(f"oo merhaba client: {time.time()}")