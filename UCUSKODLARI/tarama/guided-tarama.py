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

if len(sys.argv) != 3:
    print("Kod kullanımı: <conn_string> <drone_id>")
    exit(1)

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

is_running = True

tarama_sayisi = 3
yapilan_tarama_sayisi = 0

#! degistirmeyi unutma
ALT = 6
DRONE_ID = int(sys.argv[2])
loc = (-35.36290790, 149.16517280, ALT)

area_meter = 10
distance_meter = 3

drone_locs = vehicle.scan_area_wpler(center_loc=loc, alt=ALT, area_meter=area_meter, distance_meter=distance_meter)
print(f"{yapilan_tarama_sayisi + 1}. tarama wp sayısı: {len(drone_locs)}")
print(f"{yapilan_tarama_sayisi + 1}. tarama alanı: {area_meter}")
print(f"{yapilan_tarama_sayisi + 1}. tarama aralık mesafesi: {distance_meter}")

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    
    home_pos = vehicle.get_pos(drone_id=DRONE_ID)
    print(f"{DRONE_ID}>> takeoff yaptı")

    current_loc = 0
    vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)

    start_time = time.time()
    while is_running:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> tarama devam ediyor...")
            print(f"{DRONE_ID}>> current_loc: {current_loc + 1}/{len(drone_locs)}")
            start_time = time.time()
        
        if vehicle.on_location(loc=drone_locs[current_loc], seq=0, sapma=1, drone_id=DRONE_ID):
            start_time = time.time()
            print(f"{DRONE_ID}>> drone {current_loc + 1} ulasti")
            if current_loc + 1 == len(drone_locs):
                yapilan_tarama_sayisi += 1
                if tarama_sayisi - yapilan_tarama_sayisi > 0:
                    print(f"{yapilan_tarama_sayisi + 1}. tarama baslıyor")
                    new_distance_meter = distance_meter / (yapilan_tarama_sayisi + 1)
                    drone_locs = vehicle.scan_area_wpler(center_loc=loc, alt=ALT, area_meter=area_meter, distance_meter=new_distance_meter)
                    current_loc = 0

                    print(f"{yapilan_tarama_sayisi + 1}. tarama wp sayısı: {len(drone_locs)}")
                    print(f"{yapilan_tarama_sayisi + 1}. tarama alanı: {area_meter}")
                    print(f"{yapilan_tarama_sayisi + 1}. tarama aralık mesafesi: {new_distance_meter}")

                    vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)
                else:
                    print(f"{DRONE_ID}>> Drone taramayı bitirdi")
                    break
            else:
                current_loc += 1
                vehicle.go_to(loc=drone_locs[current_loc], alt=ALT, drone_id=DRONE_ID)
                print(f"{DRONE_ID}>> {current_loc + 1}/{len(drone_locs)}. konuma gidiyor...")
    
    print("Kalkısa donuyor")
    
    vehicle.go_to(loc=home_pos, alt=ALT, drone_id=DRONE_ID)
    while is_running:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> kalkısa donuyor...")
            start_time = time.time()
        
        if vehicle.on_location(loc=home_pos, seq=0, sapma=1, drone_id=DRONE_ID):
            vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
            break
    
    print("Gorev Tamamnaldi")
        
        

except KeyboardInterrupt:
    print("Exiting...")
    failsafe(vehicle)

except Exception as e:
    failsafe(vehicle)
    print(e)

finally:
    vehicle.vehicle.close()
