import time
import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle

vehicle = Vehicle(sys.argv[1])

start_time = time.time()

try:
    for i in vehicle.drone_ids:
        vehicle.set_mode(mode="RTL", drone_id=i)

except KeyboardInterrupt:
    print("Exiting...")

except Exception as e:
    print(e)

finally:
    vehicle.vehicle.close()
