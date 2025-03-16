import time
import serial.tools.list_ports
import sys
import socket


class TCP_Client:
    def __init__(self, recv_ip, recv_port):
        if recv_ip == "" or recv_port == "":
            print("Sunucu IP adresi veya port numarası boş olamaz!")
            sys.exit(1)

        self.recv_ip = recv_ip
        self.recv_port = recv_port
        self.client = self.connect_client()
    
    def connect_client(self, recv_ip = None, recv_port = None):
        """Sunucuya bağlanır."""
        if recv_ip == None:
            recv_ip = self.recv_ip
        if recv_port == None:
            recv_port = self.recv_port

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (recv_ip, int(recv_port))  # Sunucu adresi ve port
        client.connect(server_address)
        print("Sunucuya bağlanıldı!")

        return client

    def send_data(self, data):
        """Sunucuya veri gönderir."""
        client = self.client
        try:
            data += "\n"
            data = data.encode('utf-8')
            client.send(data)
        except Exception as e:
            print(f"Hata: {e}")
        
class Serial_Control:
    def __init__(self):
        self.ser = self.connect_serial()
    
    def connect_serial(self):
        """Seri porta bağlanır."""
        seri_portlar = serial.tools.list_ports.comports()
        seri_port = ""
        print("Seri portlar listelendi.")
        for port in seri_portlar:
            if "ch340" in port.description.lower():
                seri_port = port.device
                break

        if seri_port == "":
            print("CH340 çevirici bulunamadı!")
            sys.exit(1)
        
        ser = serial.Serial(seri_port, 9600)  # Arduino'nun bağlı olduğu portu ve baud rate'i belirle
        print("Bağlantı sağlandı:", ser.name)
        return ser
    
    def read_value(self):
        """Seri porttan veri okur."""
        ser = self.ser
        ser_value = ""
        if ser.in_waiting > 0:
            ser_value = str(ser.readline().decode("utf-8", errors='ignore')).strip()

        return ser_value
    

# Seri port ayarları
if len(sys.argv) != 3:
    print("Kullanım: python3 value_read_and_send.py <sunucu_ip> <sunucu_port>")
    sys.exit(1)

recv_ip = sys.argv[1]
recv_port = int(sys.argv[2])


try:
    client = TCP_Client(recv_ip=recv_ip, recv_port=recv_port)
    serial = Serial_Control()

    start_time = time.time()
    while True:
        try:
            ser_val = serial.read_value()
            if ser_val != "":
                x_value = ser_val.split("|")[0].strip()
                y_value = ser_val.split("|")[1].strip()

                i = 0
                while 4 - len(x_value) > i:
                    x_value = "0" + x_value
                    i += 1

                if x_value == "000":
                    x_value += "0"

                i = 0
                while 4 - len(y_value) > i:
                    y_value = "0" + y_value
                    i += 1
                
                if y_value == "000":
                    y_value += "0"

                if time.time() - start_time >= 3:
                    print(f"X: {x_value}, Y: {y_value}")
                    start_time = time.time()
                send_data = str(x_value) + "|" + str(y_value) + "\n"
                client.send_data(send_data)

        except Exception as e:
            print(f"Hata: {e}")
            break

except KeyboardInterrupt:
    print("\nBağlantı kapatılıyor...")

except Exception as e:
    print(f"Hata: {e}")

finally:
    if "client" in locals():
        client.client.close()