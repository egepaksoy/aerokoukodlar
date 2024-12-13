import time
import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import *
import threading

if len(sys.argv) != 2:
    print("Usage: python main.py <connection_string>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

try:
    vehicle.set_mode(mode="GUIDED")
    vehicle.arm_disarm(arm=True)
    print(vehicle.get_pos())
    time.sleep(10)
    print(vehicle.get_pos())
    vehicle.arm_disarm(arm=False)
        
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")

finally:
    vehicle.vehicle.close()
