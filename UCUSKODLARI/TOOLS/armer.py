import time
import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import *
import threading

if len(sys.argv) != 3:
    print("Usage: python main.py <connection_string> <drone_id>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])
DRONE_ID = int(sys.argv[2])

start_time = time.time()

try:
    vehicle.set_mode(mode="GUIDED", drone_id=DRONE_ID)
    vehicle.arm_disarm(arm=True, drone_id=DRONE_ID)
        
    print("Görev tamamlandı")

except KeyboardInterrupt:
    print("Exiting...")

finally:
    vehicle.vehicle.close()
