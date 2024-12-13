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

ALT_1 = 7
ALT_2 = 5
top_birakma_alt = 3
DRONE_1_ID = 1
DRONE_2_ID = 3
loc = (40.7121505, 30.0245339, ALT_1)
drone_pos = [loc] # ilk waypoint dummy wp
scan_wps = vehicle.scan_area_wpler(loc[0], loc[1], ALT_1, area_meter=5, distance_meter=2)
drone_pos += scan_wps

end_mode = "RTL"

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
            vehicle.set_mode(mode="RTL", drone_id=DRONE_1_ID)
            print(f"{DRONE_1_ID}>> gorevi bitirdi")
            break
    
    print(f"{DRONE_2_ID}>> goreve baslıyor")
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_2_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_2_ID)
    vehicle.takeoff(ALT_2, drone_id=DRONE_2_ID)
    
    print(f"{DRONE_2_ID}>> takeoff yaptı")

    loc_2 = (loc[0], loc[1], ALT_2)
    drone_pos = (loc_2, loc_2)
    vehicle.send_all_waypoints(drone_id=DRONE_2_ID, wp_list=drone_pos)

    vehicle.set_mode(mode="AUTO", drone_id=DRONE_2_ID)

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_2_ID}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone_pos[-1], seq=len(drone_pos) - 1, sapma=1, drone_id=DRONE_2_ID):
            print(f"{DRONE_2_ID}>> drone hedefe ulasti")
            vehicle.set_mode(mode="GUIDED", drone_id=DRONE_2_ID)
            current_pos = vehicle.get_pos(drone_id=DRONE_2_ID)
            vehicle.go_to(lat=current_pos[0], lon=current_pos[1], alt=top_birakma_alt, drone_id=DRONE_2_ID)

            start_time = time.time()
            while vehicle.get_pos(drone_id=DRONE_2_ID)[2] <= top_birakma_alt * 1.1:
                if time.time() - start_time >= 2:
                    print(f"{DRONE_2_ID}>> top bırakma yüksekliğine iniyor...")
                    start_time = time.time()

            print(f"{DRONE_2_ID}>> top bıraktı")
            vehicle.set_mode(mode="RTL", drone_id=DRONE_2_ID)
            print(f"{DRONE_2_ID}>> gorevi bitirdi")
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