import time
import sys
sys.path.append('../pymavlink_custom')
from pymavlink_custom import *
import threading

def failsafe(vehicle):
    def failsafe_drone_id(vehicle, drone_id):
        print(f"{drone_id}>> Failsafe alıyor")
        vehicle.set_mode(mode="RTL", drone_id=drone_id)

    thraeds = []
    for d_id in vehicle.drone_ids:
        thrd = threading.Thread(target=failsafe_drone_id, args=(vehicle, d_id))
        thrd.start()
        thraeds.append(thrd)

    for t in thraeds:
        t.join()

    print(f"Dronlar {vehicle.drone_ids} Failsafe aldi")

if len(sys.argv) != 3:
    print("Usage: python main.py <connection_string> <drone_id>")
    sys.exit(1)

#! gorev dosyası oluşturma
with open("./gorev_dosyaları/ates_konum.txt", "w+") as file:
    file.close()

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

ALT = 5
DRONE_ID = int(sys.argv[2]) # drone id

try:
    while True:
        if vehicle.get_mode(drone_id=DRONE_ID) == "GUIDED":
            vehicle.set_mode(mode="POSHOLD", drone_id=DRONE_ID)
        else:
            vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
        
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")
    failsafe(vehicle)

except Exception as e:
    failsafe(vehicle)
    print(e)

finally:
    vehicle.vehicle.close()

