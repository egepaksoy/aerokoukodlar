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

if len(sys.argv) != 3:
    print("Usage: python main.py <connection_string> <drone_id>")
    sys.exit(1)

#! gorev dosyası oluşturma
with open("./gorev_dosyaları/ates_konum.txt", "w+") as file:
    file.close()

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

ALT = 5
DRONE_ID = int(sys.argv[2]) # drone id

loc = (40.7119682, 30.024605, ALT)
#loc = (-35.36320285, 149.16522936, ALT)

drone_pos = [loc] # ilk waypoint dummy wp

scan_wps = vehicle.scan_area_wpler(loc=loc, alt=ALT, area_meter=5, distance_meter=1)
drone_pos += scan_wps

end_mode = "LAND"

DETECTED = False
SCREEN_RAT = (640, 480)
ALT_MET = 640

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    takeoff_pos = vehicle.get_pos(drone_id=DRONE_ID)
    
    print(f"{DRONE_ID}>> takeoff yaptı")

    vehicle.send_all_waypoints(drone_id=DRONE_ID, wp_list=drone_pos)

    vehicle.set_mode(mode="AUTO", drone_id=DRONE_ID)

    # GOREV
    start_time = time.time()
    while True:
        if time.time() - start_time > 3:
            print(f"{DRONE_ID}>> ucus devam ediyor...")
            start_time = time.time()
    
        #! algılanan konumu hesaplama
        if DETECTED == False:
            with open("./gorev_dosyaları/ates_konum.txt", "r") as ates_file:
                for line in ates_file:
                    if line and len(line.strip()) != 0:
                        print("Ates algılandı")
                        drone_current_pos = vehicle.get_pos(drone_id=DRONE_ID)
                        drone_yaw = vehicle.get_yaw(drone_id=DRONE_ID)

                        uzaklik, aci = calc_hipo_angle(SCREEN_RAT, get_pixel_pos(line), drone_current_pos[2], drone_yaw, ALT_MET)

                        ates_posizyonu = calc_location(uzaklik, aci, drone_current_pos[0], drone_current_pos[1])

                        DETECTED = True
                        print(f"Ateş konumu: {ates_posizyonu}")
        
        if vehicle.on_location(loc=drone_pos[-1], seq=len(drone_pos) - 1, sapma=0.75, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone taramayı tamamladı")
            break
    
    if DETECTED:
        #! algılanan konuma gitme
        print(f"{DRONE_ID}>> ates konumuna gidiyor...")
        vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
        vehicle.go_to(loc=ates_posizyonu, alt=ALT, drone_id=DRONE_ID)

        while True:
            if time.time() - start_time > 2:
                print(f"{DRONE_ID}>> atese gidiyor...")
                start_time = time.time()
            
            if vehicle.on_location(loc=ates_posizyonu, seq=0, sapma=1, drone_id=DRONE_ID):
                print(f"{DRONE_ID}>> ates konumuna gelindi")

                print("3sn beklemiyor...")
                time.sleep(3)

                break
    
    # MANUEL RTL
    print(f"{DRONE_ID}>> drone inişe geçti")
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.go_to(loc=takeoff_pos, alt=ALT, drone_id=DRONE_ID)
    while True:
        if time.time() - start_time > 3:
            print(f"{DRONE_ID}>> drone inise geciyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=takeoff_pos, seq=0, sapma=1, drone_id=DRONE_ID):
            print(f"{DRONE_ID}>> drone iniyor")
            vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
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
