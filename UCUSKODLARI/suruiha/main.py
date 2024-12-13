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

def takeoff(vehicle, drone_id):
    vehicle.set_mode(mode="GUIDED", drone_id=drone_id)
    vehicle.arm_disarm(arm=True, drone_id=drone_id)
    vehicle.multiple_takeoff(ALT, drone_id)
    
    start_time = time.time()
    vehicle_alt = vehicle.get_pos(drone_id)[2]
    while vehicle_alt < ALT * 0.9 and is_running:
        vehicle_alt = vehicle.get_pos(drone_id)[2]
        if time.time() - start_time > 2:
            print(f"{drone_id}>> takeoff yuksekligi: {vehicle_alt}")
            start_time = time.time()
    
    if is_running:
        print(f"{drone_id}>> takeoff tamamladı")

def add_waypoints(vehicle, drone_id, waypoints):
    vehicle.send_all_waypoints(waypoints, drone_id)
    print(f"{drone_id}>> waypointler atildi")

def drone_miss(vehicle, drone_id, end_pos):
    print(f"{drone_id}>> drone goreve basladi")
    drone_pos = [end_pos, end_pos]
    vehicle.send_all_waypoints(drone_id=drone_id, wp_list=drone_pos)

    vehicle.set_mode(mode="AUTO", drone_id=drone_id)

    start_time = time.time()
    while is_running:
        if time.time() - start_time > 5:
            print(f"{drone_id}>> ucus devam ediyor...")
        
        if vehicle.on_location(loc=end_pos, seq=1, sapma=1, drone_id=drone_id):
            print(f"{drone_id}>> drone hedefe ulasti")
            #! RTL -> LAND
            vehicle.set_mode(mode="RTL", drone_id=drone_id)
            return


vehicle = Vehicle(sys.argv[1])

start_time = time.time()

is_running = True

ALT = 5
drone_1_pos = (-35.36305907, 149.16518658, ALT)
drone_2_pos = (-35.36301891, 149.16522457, ALT)
drone_3_pos = (-35.36294663, 149.16538495, ALT)

try:
    for i in vehicle.drone_ids:
        vehicle.set_mode(mode="GUIDED", drone_id=i)

    takeoff_thrds = []
    for i in vehicle.drone_ids:
        thrd = threading.Thread(target=takeoff, args=(vehicle, i))
        thrd.start()
        takeoff_thrds.append(thrd)
    
    strtime = time.time()
    for i in takeoff_thrds:
        if time.time() - strtime > 2:
            print(i)
        if i.is_alive():
            i.join()
    
    print("Dronlar takeoff yaptı")

    drone_miss_thrds = []
    for drone_id in vehicle.drone_ids:
        print(f"{drone_id}>> drone goreve hazirlaniyor")
        drone_thrd = threading.Thread(target=drone_miss, args=(vehicle, drone_id, getattr(sys.modules[__name__], f"drone_{drone_id}_pos")))
        drone_thrd.start()
        drone_miss_thrds.append(drone_thrd)
    
    for i in drone_miss_thrds:
        if (i.is_alive()):
            i.join()
    
    print("Görev tamamlandı")
    

except KeyboardInterrupt:
    print("Exiting...")
    is_running = False
    failsafe(vehicle)

except Exception as e:
    is_running = False
    failsafe(vehicle)
    print(e)

finally:
    is_running = False
    vehicle.vehicle.close()