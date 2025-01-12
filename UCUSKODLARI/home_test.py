import threading
import time
import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle

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

go_pos_x = 0
go_pos_y = 0

try:
    vehicle.set_mode(mode="GUIDED")
    vehicle.arm_disarm(arm=True)
    vehicle.takeoff(alt=5)

    start_time = time.time()
    vehicle.set_guided_speed(speed=1000)
    vehicle.go_to(loc=(40.711, 30.02), alt=5)
    while True:
        if time.time() - start_time > 3:
            current_pos = vehicle.get_pos()
            print("current: ", current_pos)
            start_time = time.time()

except KeyboardInterrupt:
    failsafe(vehicle)
    print("Exiting...")

except Exception as e:
    failsafe(vehicle)
    print(e)

finally:
    vehicle.vehicle.close()