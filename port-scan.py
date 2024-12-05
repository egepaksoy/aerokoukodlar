
import serial.tools.list_ports

def connected_ports():
    ports = serial.tools.list_ports.comports()
    if ports:
        for port in ports:
            print(f"- {port.device} ({port.description})")
    else:
        print("Hiçbir COM portu bağlı değil.")

connected_ports()