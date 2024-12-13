import time
import sys
sys.path.append('../pymavlink_custom')
from pymavlink_custom import *
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

#! gorev dosyası oluşturma
with open("./gorev_dosyaları/ates_konum.txt", "w+") as file:
    file.close()

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

ALT_1 = 5
ALT_2 = 7
top_birakma_alt = 4

DRONE_1_ID = 3
DRONE_2_ID = 1

loc = (-35.36302115, 149.16520621, ALT_1)

drone_pos = [loc] # ilk waypoint dummy wp

scan_wps = vehicle.scan_area_wpler(loc[0], loc[1], ALT_1, area_meter=5, distance_meter=2)
drone_pos += scan_wps

DETECTED = False
SCREEN_RAT = (640, 480)
ALT_MET = 640

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
        if time.time() - start_time > 3:
            print(f"{DRONE_1_ID}>> ucus devam ediyor...")
            start_time = time.time()

        #! ates konumunu hesaplama kodu
        if DETECTED == False:
            with open("./gorev_dosyaları/ates_konum.txt", "r") as ates_file:
                for line in ates_file:
                    if line and len(line.strip()) != 0:
                        print("Ates algılandı")
                        drone_current_pos = vehicle.get_pos(drone_id=DRONE_1_ID)
                        drone_yaw = vehicle.get_yaw(drone_id=DRONE_1_ID)

                        uzaklik, aci = calc_hipo_angle(SCREEN_RAT, get_pixel_pos(line), drone_current_pos[2], drone_yaw, ALT_MET)

                        ates_posizyonu = calc_location(uzaklik, aci, drone_current_pos[0], drone_current_pos[1])

                        DETECTED = True
                        print(f"Ateş konumu: {ates_posizyonu}")
        
        if vehicle.on_location(loc=drone_pos[-1], seq=len(drone_pos) - 1, sapma=1, drone_id=DRONE_1_ID):
            print(f"{DRONE_1_ID}>> taramayı bitirdi")
            vehicle.set_mode(mode="GUIDED", drone_id=DRONE_1_ID)
            vehicle.go_to(lat=drone1_takeoff[0], lon=drone1_takeoff[1], alt=vehicle.get_pos(drone_id=DRONE_1_ID)[2], drone_id=DRONE_1_ID)
            break

    while True:
        if time.time() - start_time > 3:
            print(f"{DRONE_1_ID}>> inise geciyor...")
            start_time = time.time()

        if vehicle.on_location(loc=drone1_takeoff, seq=0, sapma=1, drone_id=DRONE_1_ID):
            print(f"{DRONE_1_ID}>> drone iniyor...")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_1_ID)
            break

    
    if DETECTED == False:
        print("Ateş algılanamadı görev iptal edildi")
        exit()

    print(f"{DRONE_2_ID}>> goreve baslıyor")
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_2_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_2_ID)

    vehicle.takeoff(ALT_2, drone_id=DRONE_2_ID)
    drone2_takeoff = vehicle.get_pos(drone_id=DRONE_2_ID)
    
    print(f"{DRONE_2_ID}>> takeoff yaptı")

    #! ates konumuna gitme kodu
    vehicle.go_to(lat=ates_posizyonu[0], lon=ates_posizyonu[1], alt=ALT_2, drone_id=DRONE_2_ID)
    print(f"{DRONE_2_ID}>> drone atese gidiyor...")

    start_time = time.time()
    while True:
        if time.time() - start_time > 2:
            print(f"{DRONE_2_ID}>> atese gidiyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=ates_posizyonu, seq=0, sapma=1, drone_id=DRONE_2_ID):
            print(f"{DRONE_2_ID}>> drone atese ulasti")
            print("3sn bekleniyor...")
            time.sleep(3)
            vehicle.go_to(lat=drone2_takeoff[0], lon=drone2_takeoff[1], alt=top_birakma_alt, drone_id=DRONE_2_ID)

            print(f"{DRONE_2_ID}>> gorevi bitirdi")
            break
    
    while True:
        if time.time() - start_time > 3:
            print(f"{DRONE_2_ID}>> inise geciyor...")
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
