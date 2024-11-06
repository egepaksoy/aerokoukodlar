import time
import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

try:
    vehicle.set_mode(mode="GUIDED", drone_id=3)
    print(f"{3}: {vehicle.get_pos(drone_id=3)}")

except KeyboardInterrupt:
    print("Exiting...")

except Exception as e:
    print(e)

finally:
    vehicle.vehicle.close()
