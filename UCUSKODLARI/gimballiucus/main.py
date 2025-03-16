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

# 1- tcp bağlantısı ile drondaki veriler alıncak
# 2- serial bağlantısı ile arduino verileri alıncak
# 3- tcp ile arduino verileri drondaki gimbale gönderilcek
# 4- goruntu işleme ekranda gösterilcek

if len(sys.argv) != 3:
    print("Usage: python main.py <connection_string> <drone_id>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

ALT = 7
DRONE_ID = int(sys.argv[2]) # drone id
target_loc = []
home_pos = []

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
    vehicle.takeoff(ALT, drone_id=DRONE_ID)
    home_pos = vehicle.get_pos(drone_id=DRONE_ID)    
    
    print(f"{DRONE_ID}>> takeoff yaptı")
    print(f"{DRONE_ID}>> hedefleri arıyor...")

    start_time = time.time()
    while True:
        if time.time() - start_time > 5:
            print(f"{DRONE_ID}>> hedefler aranıyor...")
            start_time = time.time()
        
        if target_loc != []:
            print(f"{DRONE_ID}>> hedef bulundu")
            break

    if target_loc != []:
        vehicle.go_to(loc=target_loc, alt=ALT, drone_id=DRONE_ID)
        print(f"{DRONE_ID}>> hedefe gidiyor")

        start_time = time.time()
        while True:
            if time.time() - start_time > 5:
                print(f"{DRONE_ID}>> hedefe gidiyor...")
                start_time = time.time()
            
            if vehicle.on_location(loc=target_loc, seq=0, sapma=1, drone_id=DRONE_ID):
                print(f"{DRONE_ID}>> hedefe ulaştı")
                print(f"{DRONE_ID}>> iniş gerçekleştiriyor")
                vehicle.set_mode(mode="LAND", drone_id=DRONE_ID)
                break
    
    else:
        vehicle.go_to(loc=home_pos, alt=ALT, drone_id=DRONE_ID)
        print(f"{DRONE_ID}>> kalkış konumuna dönüyor...")

        start_time = time.time()
        while True:
            if time.time() - start_time > 5:
                print(f"{DRONE_ID}>> kalkış konumuna dönüyor...")
                start_time = time.time()
            
            if vehicle.on_location(loc=home_pos, seq=0, sapma=1, drone_id=DRONE_ID):
                print(f"{DRONE_ID}>> iniş gerçekleşiyor")
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