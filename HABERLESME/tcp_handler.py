import queue
import socket
import threading
from threading import Thread

class TCPClient():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False
        self.running = True

        self.connect()

        self.data_queue = queue.Queue()

    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
            self.connected = True

            Thread(target=self.receive_data, daemon=True).start()

            print(f"{self.ip} adresine bağlandı ve veri akışı başlatıldı")
            
        except Exception as e:
            self.running = False
            print(f"Client>> Connection failed: {e}")

    def send_data(self, data):
        try:
            if self.connected:
                self.socket.sendall(data.encode())
            else:
                print("Client>> server'a bağlantı sağlanamadı")

        except Exception as e:
            print(f"Send failed: {e}")

    def receive_data(self, buffer_size=1024):
        while self.running:
            try:
                data = self.socket.recv(buffer_size).decode()
                if not data:
                    break
                self.data_queue.put(data)

            except Exception as e:
                print(f"Client>> Receive failed: {e}")
                break

    def get_data(self):
        try:
            return self.data_queue.get_nowait()  # En son veriyi al, boşsa hata verme
        except queue.Empty:
            return None

    def close(self):
        self.running = False
        self.socket.close()

class TCPServer:
    def __init__(self, ip, port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, self.port))

        self.server_socket.listen(5)  # Maksimum 5 client
        
        self.data_queue = queue.Queue()  # Gelen verileri saklamak için Queue
        self.running = True  # Sunucunun çalışıp çalışmadığını kontrol eden flag
        self.connected_addrs = []
        self.connected_clients = []

        self.start()

    def start(self):
        print(f"Server port {self.port} ile dinlemeye basladi")
        Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"{addr} adresinden yeni baglanti")
            self.connected_addrs.append(addr)
            self.connected_clients.append(client_socket)
            Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break  # Client bağlantıyı kapattıysa çık
                self.data_queue.put(data)  # Gelen veriyi queue'ya ekle
                
            except Exception as e:
                print(f"Server>> Client connection error: {e}")
                break
        client_socket.close()

    def send_data(self, data, addr=None):
        try:
            if addr == None:
                for client in self.connected_clients:
                    client.sendall(data.encode())
            else:
                index_of_addr = self.connected_addrs.index(addr)
                self.connected_clients[index_of_addr].sendall(data.encode())

        except Exception as e:
            print(f"Server>> veri göndermede hata çıktı: {e}")
    
    def get_addrs(self):
        return self.connected_addrs
    
    def get_data(self):
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
        self.server_socket.close()

