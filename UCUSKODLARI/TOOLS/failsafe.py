import sys
sys.path.append('./pymavlink_custom')
from pymavlink_custom import Vehicle
import threading
import serial.tools.list_ports

def connected_ports():
    ports = serial.tools.list_ports.comports()
    if ports:
        for port in ports:
            print(f"- {port.device} ({port.description})")
    else:
        print("Hiçbir COM portu bağlı değil.")

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

if len(sys.argv) > 1:
    vehicle = Vehicle(address=sys.argv[1], on_flight=False)
else:
    vehicle = Vehicle()

try:
    failsafe(vehicle)

except KeyboardInterrupt:
    print("Exiting...")

except Exception as e:
    print(e)

finally:
    vehicle.vehicle.close()
