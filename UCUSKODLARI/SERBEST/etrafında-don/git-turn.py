import time
import sys
sys.path.append('../../pymavlink_custom')
from pymavlink_custom import Vehicle
import threading

def failsafe(vehicle, home_pos=None):
    def failsafe_drone_id(vehicle, drone_id, home_pos=None):
        if home_pos == None:
            print(f"{drone_id}>> Failsafe alıyor")
            vehicle.set_mode(mode="RTL", drone_id=drone_id)

        # guıdedli rtl
        else:
            print(f"{drone_id}>> Failsafe alıyor")
            vehicle.set_mode(mode="GUIDED", drone_id=drone_id)

            alt = 5
            
            vehicle.go_to(loc=home_pos, alt=alt, drone_id=DRONE_ID)

            start_time = time.time()
            while True:
                if time.time() - start_time > 3:
                    print(f"{drone_id}>> RTL Alıyor...")
                    start_time = time.time()

                if vehicle.on_location(loc=home_pos, seq=0, sapma=1, drone_id=DRONE_ID):
                    print(f"{DRONE_ID}>> iniş gerçekleşiyor")
                    vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
                    break

    thraeds = []
    for d_id in vehicle.drone_ids:
        args = (vehicle, d_id)
        if home_pos != None:
            args = (vehicle, d_id, home_pos)

        thrd = threading.Thread(target=failsafe_drone_id, args=args)
        thrd.start()
        thraeds.append(thrd)


    for t in thraeds:
        t.join()

    print(f"{vehicle.drone_ids} id'li Drone(lar) Failsafe aldi")

if len(sys.argv) != 3:
    print("Usage: python main.py <connection_string> <drone_id>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

ALT = 5
DRONE_ID = int(sys.argv[2]) # drone id
#TODO: konumu degistir
loc = (40.7121218, 30.0245587, ALT)
drone_pos = (loc, loc) # ilk waypoint dummy wp

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    takeoff_pos = vehicle.get_pos(drone_id=DRONE_ID)

    home_pos = vehicle.get_pos(drone_id=DRONE_ID)
    
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
            break
    
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)

    #! burdaki hız değeri gerçekten oluyor
    vehicle.turn_around(default_speed=30, drone_id=DRONE_ID)

    print("Donme bitti")
    time.sleep(1)
    
    vehicle.go_to(loc=takeoff_pos, alt=ALT, drone_id=DRONE_ID)
    print(f"{DRONE_ID}>> drone donuyor")

    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> inis devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=takeoff_pos, seq=0, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone iniyor")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
            break
    
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")
    if "home_pos" in locals():
        failsafe(vehicle, home_pos)
    else:
        failsafe(vehicle)

except Exception as e:
    if "home_pos" in locals():
        failsafe(vehicle, home_pos)
    else:
        failsafe(vehicle)
    print(e)

finally:
    vehicle.vehicle.close()