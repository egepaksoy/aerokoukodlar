import time
import sys
sys.path.append('../pymavlink_custom')
from pymavlink_custom import Vehicle
import threading

def get_errors(vehicle):
    def scan_errors(vehicle):
        while on_flight:
            print(f"{vehicle.error_messages()}")
            threading.Event().wait(1)
    
    thrd = threading.Thread(target=scan_errors, args=(vehicle,))
    thrd.start()

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
on_flight = True

get_errors(vehicle)

start_time = time.time()

drone_1_landing = False
drone_2_landing = False

ALT = 5
DRONE_1_ID = 1
DRONE_2_ID = 2
loc1 = (-35.36305893, 149.16516251, ALT)
loc2 = (-35.36295790, 149.16525463, ALT)
drone_1_pos = (loc1, loc1) # ilk waypoint dummy wp
drone_2_pos = (loc2, loc2) # ilk waypoint dummy wp

try:
    ############# drone1 takeoff ###############
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_1_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_1_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_1_ID)
    
    print(f"{DRONE_1_ID}>> takeoff yaptı")
    ############## drone2 takeoff ###########
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_2_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_2_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_2_ID)
    
    print(f"{DRONE_2_ID}>> takeoff yaptı")
    ############## takeoff tamam #############

    ########### drone1 waypoint ##########
    vehicle.send_all_waypoints(drone_id=DRONE_1_ID, wp_list=drone_1_pos)
    ########### drone2 waypoint ##########
    vehicle.send_all_waypoints(drone_id=DRONE_2_ID, wp_list=drone_2_pos)

    ########### dronlar auto yapildi ##########
    vehicle.set_mode(mode="AUTO", drone_id=DRONE_1_ID)
    vehicle.set_mode(mode="AUTO", drone_id=DRONE_2_ID)

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print("ucuslar devam ediyor...")
            start_time = time.time()
        
        #! thread yapılacak
        #### drone1 iniyor #########
        if vehicle.on_location(loc=drone_1_pos[1], seq=1, sapma=1, drone_id=DRONE_1_ID):
            print(f"{DRONE_1_ID}>> drone hedefe ulasti")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_1_ID)
            drone_1_landing = True

        #### drone2 iniyor #########
        if vehicle.on_location(loc=drone_2_pos[1], seq=1, sapma=1, drone_id=DRONE_2_ID):
            print(f"{DRONE_2_ID}>> drone hedefe ulasti")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_2_ID)
            drone_2_landing = True
        
        if drone_1_landing and drone_2_landing:
            break

    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")
    failsafe(vehicle)

except Exception as e:
    failsafe(vehicle)
    print(e)

finally:
    on_flight = False
    vehicle.vehicle.close()
