import socket
import threading
import sys
import queue
import serial

def send_to_arduino(ser, data):
    """Arduino'ya seri port üzerinden veri gönderir."""
    try:
        # Seri portu aç
        x_data = data.strip().split("|")[0]
        y_data = data.strip().split("|")[1]

        x_data = str((int(x_data) + 1) * 180 / 1023)
        y_data = str((int(y_data) + 1) * 180 / 1023)

        data = f"{x_data}|{y_data}\n"
        
        ser.write(data.encode('utf-8'))

    except serial.SerialException as e:
        print(f"Seri port hatası: {e}")
    except Exception as e:
        print(f"Hata: {e}")


def handle_client_connection(client_socket):
    """İstemciden gelen veriyi okur ve konsola yazdırır."""
    global data_queue

    client_socket.settimeout(2)

    while not stop_event.is_set():
        try:
            data = client_socket.recv(1024)  # Maksimum 1024 byte veri al
            if not data:
                break  # Bağlantı kesilmiş
            if "\n" in data.decode("utf-8"):
                data_queue = data.decode('utf-8').strip()[0:9]
        
        except socket.timeout:
            continue

        except Exception as e:
            print(f"Hata: {e}")
            break
    
    print(f"Bağlantı kapandı")
    client_socket.close()

def start_server(port):
    """TCP sunucusunu başlatır ve istemcilerle bağlantıyı yönetir."""
    global data_queue

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', int(port)))  # Tüm IP adreslerinden bağlantıyı kabul eder, port 12345
    server.listen(5)  # Maksimum 5 istemci kuyruğu
    print("Sunucu başlatıldı, bağlantı bekleniyor...")

    while not stop_event.is_set():
        client_socket, addr = server.accept()  # Yeni istemci bağlandı
        print(f"Bağlanan istemci: {addr}")
        # İstemci bağlantısını işlemek için bir iş parçacığı başlat
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()

def is_data_valid(data):
    """Gelen verinin geçerli olup olmadığını kontrol eder."""
    try:
        if "|" in data:
            x_value = data.split("|")[0].strip()
            y_value = data.split("|")[1].strip()

            if len(x_value) == 4 and len(y_value) == 4:
                pass
            else:
                return False

            if x_value.isdigit() and y_value.isdigit():
                return True
            else:
                return False
        else:
            return False
    except:
        return False

def return_normal(value):
    value = str(value)
    for i in str(value):
        if i == "0":
            continue
        else:
            return value[value.index(i):]

    return "0"


if len(sys.argv) != 3:
    print("Kullanım: python3 tcp_servo_kontrol.py <port> <usb_port>")
    sys.exit(1)

port = int(sys.argv[1])
usb_port = sys.argv[2]

stop_event = threading.Event()

try:
    data_queue = ""
    servo_thread = threading.Thread(target=start_server, args=(port,))
    servo_thread.start()

    ser = serial.Serial(usb_port, 9600, timeout=1)

    data = ""
    while not stop_event.is_set():
        if is_data_valid(data_queue):
            data = data_queue
            
            x_value = int(return_normal(data.split("|")[0]))
            y_value = int(return_normal(data.split("|")[1]))

            print("X:", int(x_value), "Y:", int(y_value))
            send_to_arduino(ser, f"{int(x_value)}|{int(y_value)}\n")

except Exception as e:
    if not stop_event.is_set():
        stop_event.set()
    print(f"Hata: {e}")

except KeyboardInterrupt:
    if not stop_event.is_set():
        stop_event.set()
    print("Cikilioyr")

finally:
    if not stop_event.is_set():
        stop_event.set()
    ser.close()
    sys.exit(1)
