import time
import threading
import sys

sys.path.append('../pymavlink_custom')
from pymavlink_custom import Vehicle


def failsafe(vehicle):
    def failsafe_drone_id(vehicle, drone_id):
        print(f"{drone_id}>> Failsafe alıyor")
        vehicle.set_mode(mode="RTL", drone_id=drone_id)

    if not stop_event.is_set():
        stop_event.set()

    thraeds = []
    for d_id in vehicle.drone_ids:
        thrd = threading.Thread(target=failsafe_drone_id, args=(vehicle, d_id))
        thrd.start()
        thraeds.append(thrd)

    for t in thraeds:
        t.join()

    print(f"Dronlar {vehicle.drone_ids} Failsafe aldi")

def takeoff_drone(vehicle, drone_values):
    DRONE_ID = drone_values["drone_id"]
    ALT = drone_values["alt"]

    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    if stop_event.is_set():
        return
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    if stop_event.is_set():
        return
    vehicle.multiple_takeoff(ALT, drone_id=DRONE_ID)
    if stop_event.is_set():
        return

    start_time = time.time()
    while vehicle.get_pos(drone_id=DRONE_ID)[2] <= ALT * 0.9 and not stop_event.is_set():
        if time.time() - start_time > 2:
            print(f"{DRONE_ID}>> takeoff yapıyor...")
            start_time = time.time()
    
    if stop_event.is_set():
        return
    
    print(f"{DRONE_ID}>> takeoff yaptı")


def drone_miss(vehicle, drone_values):
    DRONE_ID = drone_values["drone_id"]
    ALT = drone_values["alt"]
    MISS_ALT = drone_values["miss_alt"]
    POS = drone_values["miss_point"]
    TAKEOFF_POS = drone_values["takeoff_pos"]

    on_second_miss = False
    current_miss = "miss_point"

    start_time = time.time()
    first_time = time.time()

    vehicle.go_to(loc=drone_values[current_miss], alt=ALT, drone_id=DRONE_ID)

    while not stop_event.is_set():
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> hedefe gidiyor...")
            start_time = time.time()
        
        if stop_event.is_set():
            break
        
        if on_second_miss == False and "second_miss_point" in drone_values:
            if time.time() - first_time >= 1.5:
                print(f"{DRONE_ID}>> Yeni bir hedef buldu oraya yöneliyor...")
                current_miss = "second_miss_point"
                vehicle.go_to(loc=drone_values[current_miss], alt=ALT, drone_id=DRONE_ID)
                on_second_miss = True

        if stop_event.is_set():
            break
        
        if vehicle.on_location(loc=drone_values[current_miss], seq=0, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone hedefe ulasti alcaliyor...")
            break
    
        if stop_event.is_set():
            break
        
    if stop_event.is_set():
        return
        
    current_pos = vehicle.get_pos(drone_id=DRONE_ID)
    
    if stop_event.is_set():
        return
    
    vehicle.go_to(loc=current_pos, alt=MISS_ALT, drone_id=DRONE_ID)
    
    if stop_event.is_set():
        return

    start_time = time.time()
    while not stop_event.is_set():
        if time.time() - start_time > 2:
            print(f"{DRONE_ID}>> {MISS_ALT} metre'ye alcaliyor")
            start_time = time.time()
    
        if stop_event.is_set():
            break
        
        if vehicle.get_pos(drone_id=DRONE_ID)[2] <= MISS_ALT * 1.1:
            print(f"{DRONE_ID}>> alçaldı top birakildi...")
            time.sleep(2)
            break

    if stop_event.is_set():
        return
    

def return_home(vehicle, drone_values):
    DRONE_ID = drone_values["drone_id"]
    ALT = drone_values["alt"]
    TAKEOFF_POS = drone_values["takeoff_pos"]

    current_pos = vehicle.get_pos(drone_id=DRONE_ID)
    vehicle.go_to(loc=current_pos, alt=ALT, drone_id=DRONE_ID)

    while not stop_event.is_set():
        if vehicle.get_pos(drone_id=DRONE_ID)[2] >= ALT * 0.9:
            break

    if stop_event.is_set():
        return

    vehicle.go_to(loc=TAKEOFF_POS, alt=ALT, drone_id=DRONE_ID)

    if stop_event.is_set():
        return

    start_time = time.time()
    while not stop_event.is_set():
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> donuş yapıyor...")
            start_time = time.time()
    
        if stop_event.is_set():
            break
        
        if vehicle.on_location(loc=TAKEOFF_POS, seq=0, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone kalkış konumuna geldi LAND alıyor...")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
            break

    if stop_event.is_set():
        return


if len(sys.argv) != 2:
    print("Usage: python main.py <connection_string>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])

stop_event = threading.Event()
start_time = time.time()

drone1_values = {"drone_id": 1, "drone_name": "Körfez", "alt": 5, "miss_point": [40.712078, 30.0245225], "takeoff_pos": []}
drone2_values = {"drone_id": 3, "drone_name": "Feniks 2", "alt": 5, "miss_alt": 3, "miss_point": [40.7121696, 30.0246091], "second_miss_point": [40.7121488, 30.0245043], "takeoff_pos": []}

try:
    takeoff_drone(vehicle=vehicle, drone_values=drone1_values)
    drone1_values["takeoff_pos"] = vehicle.get_pos(drone_id=drone1_values["drone_id"])

    vehicle.go_to(loc=drone1_values["miss_point"], alt=drone1_values["alt"], drone_id=drone1_values["drone_id"])
    print(f"{drone1_values["drone_id"]}>> hedefe gidiyor...")

    start_time = time.time()
    while not stop_event.is_set():
        if time.time() - start_time > 5:
            print(f"{drone1_values["drone_id"]}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone1_values["miss_point"], seq=0, sapma=1, drone_id=drone1_values["drone_id"]):
            print(f"{drone1_values["drone_id"]}>> drone hedefe ulasti")
            print(f"{drone1_values["drone_id"]}>> tarama yapiyor...")
            break
    
    time.sleep(1)
    vehicle.turn_around(drone_id=drone1_values["drone_id"])
    time.sleep(1)
    print(f"{drone1_values["drone_id"]}>> taramayi bitirdi")

    print(f"{drone1_values["drone_id"]}>> iniyor...")
    return_home(vehicle=vehicle, drone_values=drone1_values)

    print("Saldiri dronlari kalkiyor...")

    drone2_takeoff = threading.Thread(target=takeoff_drone, args=(vehicle, drone2_values))

    drone2_takeoff.start()

    if stop_event.is_set():
        sys.exit(1)

    while not stop_event.is_set():
        if not drone2_takeoff.is_alive():
            break

    drone2_values["takeoff_pos"] = vehicle.get_pos(drone_id=drone2_values["drone_id"])
    print("Saldiri dronlari hedefe gidiyor...")

    drone2_miss = threading.Thread(target=drone_miss, args=(vehicle, drone2_values))
    drone2_miss.start()

    if stop_event.is_set():
        sys.exit(1)

    while not stop_event.is_set():
        if not drone2_miss.is_alive():
            break

    print(f"dronelar takeoff konumua dönüyor...")
    
    drone2_land = threading.Thread(target=return_home, args=(vehicle, drone2_values))

    drone2_land.start()

    while not stop_event.is_set():
        if not drone2_land.is_alive():
            break
    
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")
    if not stop_event.is_set():
        stop_event.set()
    failsafe(vehicle)

except Exception as e:
    if not stop_event.is_set():
        stop_event.set()
    failsafe(vehicle)
    print(e)

finally:
    if not stop_event.is_set():
        stop_event.set()
    vehicle.vehicle.close()

