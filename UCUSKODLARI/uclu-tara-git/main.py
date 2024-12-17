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

def takeoff_drone(vehicle, drone_values):
    DRONE_ID = drone_values["drone_id"]
    ALT = drone_values["alt"]

    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.multiple_takeoff(ALT, drone_id=DRONE_ID)

    start_time = time.time()
    while vehicle.get_pos(drone_id=DRONE_ID)[2] <= ALT * 0.9 and is_running:
        if time.time() - start_time > 2:
            print(f"{DRONE_ID}>> takeoff yapıyor...")
            start_time = time.time()
    
    print(f"{DRONE_ID}>> takeoff yaptı")

def drone_miss(vehicle, drone_values):
    DRONE_ID = drone_values["drone_id"]
    ALT = drone_values["alt"]
    MISS_ALT = drone_values["miss_alt"]
    POS = drone_values["miss_point"]
    TAKEOFF_POS = drone_values["takeoff_pos"]

    on_second_miss = False

    start_time = time.time()
    first_time = time.time()

    vehicle.go_to(lat=drone_values["miss_point"][0], lon=drone_values["miss_point"][1], alt=ALT, drone_id=DRONE_ID)

    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> hedefe gidiyor...")
            start_time = time.time()
        
        if on_second_miss == False and "second_miss_point" in drone_values:
            if time.time() - first_time > 3:
                print(f"{DRONE_ID}>> Yeni bir hedef buldu oraya yöneliyor...")
                vehicle.go_to(lat=drone_values["second_miss_ponit"][0], lon=drone_values["second_miss_point"][1], alt=ALT, drone_id=DRONE_ID)
                on_second_miss = True

        
        if on_second_miss:
            if vehicle.on_location(loc=drone_values["second_miss_point"], seq=0, sapma=1, drone_id=DRONE_ID):
                print(f"{DRONE_ID}>> drone hedefe ulasti alcaliyor...")
                break
        
        else:
            if vehicle.on_location(loc=drone_values["miss_point"], seq=0, sapma=1, drone_id=DRONE_ID):
                print(f"{DRONE_ID}>> drone hedefe ulasti alcaliyor...")
                break
    
    current_pos = vehicle.get_pos(drone_id=DRONE_ID)
    vehicle.go_to(lat=current_pos[0], lon=current_pos[1], alt=MISS_ALT)

    start_time = time.time()
    while True:
        if time.time() - start_time > 2:
            print(f"{DRONE_ID}>> alçalıyor...")
            start_time = time.time()
        
        if vehicle.get_pos(drone_id=DRONE_ID)[2] <= MISS_ALT * 1.1:
            print(f"{DRONE_ID}>> alçaldı top birakip kalkış konumuna dönüyor...")
            time.sleep(2)
            break
    
    vehicle.go_to(lat=TAKEOFF_POS[0], lon=TAKEOFF_POS[1], alt=ALT)

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> hedefe gidiyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=TAKEOFF_POS, seq=0, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone kalkış konumuna geldi LAND alıyor...")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
            break


if len(sys.argv) != 2:
    print("Usage: python main.py <connection_string>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])

is_running = True
start_time = time.time()

drone1_values = {"drone_id": 1, "drone_name": "Körfez", "alt": 7, "miss_point": [40.7120913, 30.02445], "takeoff_pos": []}
drone2_values = {"drone_id": 2, "drone_name": "Feniks 1", "alt": 5, "miss_alt": 3, "miss_point": [40.7120913, 30.02445], "takeoff_pos": []}
drone3_values = {"drone_id": 3, "drone_name": "Feniks 2", "alt": 4, "miss_alt": 3, "miss_point": [40.7120913, 30.02445], "second_miss_point": [40.321, 30.02], "takeoff_pos": []}

try:
    takeoff_drone(vehicle=vehicle, drone_values=drone1_values)
    drone1_values["takeoff_pos"] = vehicle.get_pos(drone_id=drone1_values["drone_id"])

    vehicle.go_to(lat=drone1_values["miss_point"][0], lon=drone1_values["miss_point"][1], alt=drone1_values["alt"], drone_id=drone1_values["drone_id"])

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{drone1_values["drone_id"]}>> ucus devam ediyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone1_values["miss_point"], seq=0, sapma=1, drone_id=drone1_values["drone_id"]):
            print(f"{drone1_values["drone_id"]}>> drone hedefe ulasti")
            print(f"{drone1_values["drone_id"]}>> tarama yapiyor...")
            break
    
    vehicle.turn_around(drone_id=drone1_values["drone_id"])
    print(f"{drone1_values["drone_id"]}>> taramayi bitirdi")
    print("Saldiri dronlari kalkiyor...")

    drone2_takeoff = threading.Thread(target=takeoff_drone, args=(vehicle, drone2_values))
    drone3_takeoff = threading.Thread(target=takeoff_drone, args=(vehicle, drone3_values))

    drone2_takeoff.start()
    drone3_takeoff.start()

    drone2_takeoff.join()
    drone3_takeoff.join()
    drone2_values["takeoff_pos"] = vehicle.get_pos(drone_id=drone2_values["drone_id"])
    drone3_values["takeoff_pos"] = vehicle.get_pos(drone_id=drone3_values["drone_id"])
    print("Saldiri dronlari hedefe gidiyor...")

    drone2_miss = threading.Thread(target=drone_miss, args=(vehicle, drone2_values))
    drone3_miss = threading.Thread(target=drone_miss, args=(vehicle, drone3_values))
    drone2_miss.start()
    drone3_miss.start()

    drone2_miss.join()
    drone3_miss.join()

    print(f"{drone1_values["drone_id"]}>> drone takeoff konumua dönüyor...")
    vehicle.go_to(lat=drone1_values["takeoff_pos"][0], lon=drone1_values["takeoff_pos"][1], alt=drone1_values["alt"])

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{drone1_values["drone_id"]}>> hedefe gidiyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone1_values["takeoff_pos"], seq=0, sapma=1, drone_id=drone1_values["drone_id"]):
            print(f"{drone1_values["drone_id"]}>> drone kalkış konumuna geldi LAND alıyor...")
            vehicle.set_mode(mode="LAND", drone_id=drone1_values["drone_id"])
            break
    
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
