import time
import sys
sys.path.append('../pymavlink_custom')
from pymavlink_custom import *
import threading

if len(sys.argv) != 2:
    print("Usage: python main.py <connection_string>")
    sys.exit(1)

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

try:
    while True:
        for i in vehicle.drone_ids:
            if vehicle.get_mode(drone_id=i) == "GUIDED":
                vehicle.set_mode(mode="POSHOLD", drone_id=i)
            else:
                vehicle.set_mode(mode="GUIDED", drone_id=i)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    vehicle.vehicle.close()

