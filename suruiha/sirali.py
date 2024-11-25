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

ALT = 4

#! BURALARID DEĞİŞTİR
LAND_MODE = "LAND"

DRONE_ID_1 = 1
DRONE_ID_2 = 3

loc1 = (40.7121167, 30.0244568, ALT)
loc2 = (40.7120076, 30.024522, ALT)
drone_pos1 = (loc1, loc1)
drone_pos2 = (loc2, loc2)

drone_1_ucus = True
drone_2_ucus = True

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID_1)
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID_2)

    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID_1)
    vehicle.takeoff(ALT, drone_id=DRONE_ID_1)
    ################ DRONE 2 ################
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID_2)
    vehicle.takeoff(ALT, drone_id=DRONE_ID_2)
    
    print("Dronlar takeoff yaptı")

    vehicle.send_all_waypoints(drone_id=DRONE_ID_1, wp_list=drone_pos1)
    vehicle.send_all_waypoints(drone_id=DRONE_ID_2, wp_list=drone_pos2)

    vehicle.set_mode(mode="AUTO", drone_id=DRONE_ID_1)
    vehicle.set_mode(mode="AUTO", drone_id=DRONE_ID_2)

    start_time = time.time()
    while is_running:
        if time.time() - start_time > 5:
            if drone_1_ucus:
                print(f"{DRONE_ID_1}>> ucus devam ediyor...")
            if drone_2_ucus:
                print(f"{DRONE_ID_2}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone_pos1[1], seq=1, sapma=1, drone_id=DRONE_ID_1):
            print(f"{DRONE_ID_1}>> drone hedefe ulasti")
            vehicle.set_mode(mode=LAND_MODE, drone_id=DRONE_ID_1)
            drone_1_ucus = False

        if vehicle.on_location(loc=drone_pos2[1], seq=1, sapma=1, drone_id=DRONE_ID_2):
            print(f"{DRONE_ID_2}>> drone hedefe ulasti")
            vehicle.set_mode(mode=LAND_MODE, drone_id=DRONE_ID_2)
            drone_2_ucus = False
        
        if drone_1_ucus == False and drone_2_ucus == False:
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
