import sys
import cv2
import socket
import numpy as np
import struct
import time
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from saldiri import Ui_MainWindow_Saldiri
from tespit_udp import Ui_MainWindow_Tespit
from hedefler import Ui_MainWindow as Ui_Hedefler


class UDPVideoStream(QThread):
    frame_received = pyqtSignal(np.ndarray)

    def __init__(self, port):
        super().__init__()
        self.udp_ip = "0.0.0.0"
        self.udp_port = port
        self.buffer_size = 65536
        self.running = True

    def run(self):  # Changed from start to run
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, self.udp_port))
        buffer = b''
        current_frame = -1

        
        while self.running:
            try:
                data, addr = sock.recvfrom(self.buffer_size)
                frame_number = struct.unpack('<L', data[:4])[0]
                packet_data = data[4:]

                if frame_number != current_frame:
                    if buffer:
                        npdata = np.frombuffer(buffer, dtype=np.uint8)
                        frame = cv2.imdecode(npdata, cv2.IMREAD_COLOR)
                        if frame is not None:
                            self.frame_received.emit(frame)
                        buffer = b''
                    current_frame = frame_number
                
                if packet_data != b'END':
                    buffer += packet_data
            except Exception as e:
                print("UDP Stream Error:", e)
                break
        
        sock.close()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class SaldiriEkrani(QMainWindow, Ui_MainWindow_Saldiri):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.ac_hedef_ekrani)

    def ac_hedef_ekrani(self):
        self.hedef_ekrani = HedefEkrani()
        self.hedef_ekrani.show()


class TespitEkrani(QMainWindow, Ui_MainWindow_Tespit):
    def __init__(self, udp_port=5000):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.ac_hedef_ekrani)
        
        self.udp_stream = UDPVideoStream(udp_port)
        self.udp_stream.frame_received.connect(self.update_frame)
        self.udp_stream.start()
        
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.video_label.width(), self.video_label.height()))
        q_img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        self.udp_stream.stop()
        event.accept()

    def ac_hedef_ekrani(self):
        self.hedef_ekrani = HedefEkrani()
        self.hedef_ekrani.show()


class HedefEkrani(QMainWindow, Ui_Hedefler):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Hedefler")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    saldiri_ekrani = SaldiriEkrani()
    tespit_ekrani = TespitEkrani(5000)  # UDP portu 5000 olarak ayarlandı
    
    saldiri_ekrani.show()
    tespit_ekrani.show()
    
    sys.exit(app.exec())
