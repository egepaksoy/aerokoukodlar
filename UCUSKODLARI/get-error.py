import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle
import time

if len(sys.argv) > 1:
	vehicle = Vehicle(address=sys.argv[1])
else:
	vehicle = Vehicle()

try:
	while True:
		print(vehicle.error_messages())
		
except KeyboardInterrupt:
	print("Exiting...")
finally:
	vehicle.vehicle.close()