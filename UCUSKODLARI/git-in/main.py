import time
import sys
sys.path.append('../pymavlink_custom')
from pymavlink_custom import Vehicle
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

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

ALT = 5
DRONE_ID = int(sys.argv[2]) # drone id
#loc = (40.7120913, 30.02445, ALT)
loc = (40.7121102, 30.0245824, ALT)
drone_pos = (loc, loc) # ilk waypoint dummy wp

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    
    print(f"{DRONE_ID}>> takeoff yaptı")

    vehicle.send_all_waypoints(drone_id=DRONE_ID, wp_list=drone_pos)

    vehicle.set_mode(mode="AUTO", drone_id=DRONE_ID)

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone_pos[1], seq=1, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone hedefe ulasti")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
            break
    
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")
    failsafe(vehicle)

except Exception as e:
    failsafe(vehicle)
    print(e)

finally:
    vehicle.vehicle.close()