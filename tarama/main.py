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

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

is_running = True

#! degistirmeyi unutma
ALT = 4
DRONE_ID = 1
loc = [40.7121378, 30.0245383, ALT]
LAND_MODE = "RTL"
drone_pos = [loc]

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    
    print("Dronlar takeoff yaptı")

    drone_pos += (vehicle.scan_area_wpler(loc[0], loc[1], ALT, area_meter=5, distance_meter=1))
    print(drone_pos)
    vehicle.send_all_waypoints(wp_list=drone_pos, drone_id=DRONE_ID)

    vehicle.set_mode(mode="AUTO", drone_id=DRONE_ID)

    start_time = time.time()
    while is_running:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone_pos[-1], seq=len(drone_pos) - 1, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone hedefe ulasti")
            vehicle.set_mode(mode=LAND_MODE, drone_id=DRONE_ID)
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