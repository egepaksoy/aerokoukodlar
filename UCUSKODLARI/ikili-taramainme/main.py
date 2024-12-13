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

ALT_1 = 5
ALT_2 = 7
top_birakma_alt = 4

DRONE_1_ID = 3
DRONE_2_ID = 1

loc = (40.7121038, 30.0245239, ALT_1)
loc2 = (40.7119591, 30.024486, ALT_1)

drone_pos = [loc] # ilk waypoint dummy wp

scan_wps = vehicle.scan_area_wpler(loc[0], loc[1], ALT_1, area_meter=5, distance_meter=2)
drone_pos += scan_wps

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_1_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_1_ID)
    vehicle.takeoff(ALT_1, drone_id=DRONE_1_ID)
    drone1_takeoff = vehicle.get_pos(drone_id=DRONE_1_ID)
    
    print(f"{DRONE_1_ID}>> takeoff yaptı")

    vehicle.send_all_waypoints(drone_id=DRONE_1_ID, wp_list=drone_pos)

    vehicle.set_mode(mode="AUTO", drone_id=DRONE_1_ID)

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_1_ID}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone_pos[-1], seq=len(drone_pos) - 1, sapma=1, drone_id=DRONE_1_ID):
            print(f"{DRONE_1_ID}>> drone hedefe ulasti")
            vehicle.set_mode(mode="GUIDED", drone_id=DRONE_1_ID)
            vehicle.go_to(lat=drone1_takeoff[0], lon=drone1_takeoff[1], alt=vehicle.get_pos(drone_id=DRONE_1_ID)[2], drone_id=DRONE_1_ID)
            print(f"{DRONE_1_ID}>> gorevi bitirdi")
            break

    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_1_ID}>> ucus devam ediyor...")
            start_time = time.time()

        if vehicle.on_location(loc=drone1_takeoff, seq=0, sapma=1, drone_id=DRONE_1_ID):
            print(f"{DRONE_1_ID}>> drone iniyor...")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_1_ID)
            break

    
    print(f"{DRONE_2_ID}>> goreve baslıyor")
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_2_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_2_ID)
    vehicle.takeoff(ALT_2, drone_id=DRONE_2_ID)
    drone2_takeoff = vehicle.get_pos(drone_id=DRONE_2_ID)
    
    print(f"{DRONE_2_ID}>> takeoff yaptı")

    vehicle.go_to(lat=loc2[0], lon=loc2[1], alt=top_birakma_alt, drone_id=DRONE_2_ID)
    print(f"{DRONE_2_ID}>> drone hedefe gidiyor...")

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_2_ID}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=loc2, seq=0, sapma=1, drone_id=DRONE_2_ID):
            print(f"{DRONE_2_ID}>> drone hedefe ulasti")
            vehicle.go_to(lat=drone2_takeoff[0], lon=drone2_takeoff[1], alt=top_birakma_alt, drone_id=DRONE_2_ID)

            print(f"{DRONE_2_ID}>> gorevi bitirdi")
            break
    
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_2_ID}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone2_takeoff, seq=0, sapma=1, drone_id=DRONE_2_ID):
            print(f"{DRONE_2_ID}>> drone iniyor...")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_2_ID)
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
