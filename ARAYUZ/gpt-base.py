import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget, QHBoxLayout, QListWidget, QComboBox)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QCamera
from PyQt5.QtCore import QTimer

class DroneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Kontrol Arayüzü")
        self.setGeometry(100, 100, 800, 600)

        self.targets = []
        self.drone_data = [
            {"konum": (0, 0), "hız": 0, "yükseklik": 0, "yaw": 0, "pitch": 0, "roll": 0, "atanan_hedefler": []},
            {"konum": (0, 0), "hız": 0, "yükseklik": 0, "yaw": 0, "pitch": 0, "roll": 0, "atanan_hedefler": []},
        ]

        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()

        self.camera_tab = QWidget()
        self.drone_tab = QWidget()
        self.target_tab = QWidget()

        self.tabs.addTab(self.camera_tab, "Kamera")
        self.tabs.addTab(self.drone_tab, "Drone Durumları")
        self.tabs.addTab(self.target_tab, "Hedefler")

        self.setCentralWidget(self.tabs)
        self.create_camera_tab()
        self.create_drone_tab()
        self.create_target_tab()

        self.update_drone_timer = QTimer()
        self.update_drone_timer.timeout.connect(self.update_drone_data)
        self.update_drone_timer.start(5000)

    def create_camera_tab(self):
        layout = QVBoxLayout()

        # Kamera görüntüsü için QVideoWidget kullanımı
        self.camera_viewfinder = QVideoWidget()
        self.camera = QCamera()
        self.camera.setViewfinder(self.camera_viewfinder)
        self.camera.start()

        self.add_target_button = QPushButton("Hedef Ekle")
        self.add_target_button.clicked.connect(self.add_random_target)

        self.remove_target_button = QPushButton("Son Hedefi Sil")
        self.remove_target_button.clicked.connect(self.remove_last_target)

        layout.addWidget(self.camera_viewfinder)
        layout.addWidget(self.add_target_button)
        layout.addWidget(self.remove_target_button)

        self.camera_tab.setLayout(layout)

    def create_drone_tab(self):
        layout = QVBoxLayout()
        self.drone_info_label = QLabel("Drone Bilgileri Güncelleniyor...")
        layout.addWidget(self.drone_info_label)
        self.drone_tab.setLayout(layout)

    def create_target_tab(self):
        layout = QVBoxLayout()
        self.target_list = QListWidget()
        self.assign_drone_combo = QComboBox()
        self.assign_drone_combo.addItems(["Drone 1", "Drone 2"])

        self.update_target_button = QPushButton("Hedefi Güncelle")
        self.update_target_button.clicked.connect(self.update_target_assignment)

        self.delete_target_button = QPushButton("Hedefi Sil")
        self.delete_target_button.clicked.connect(self.delete_selected_target)

        layout.addWidget(self.target_list)
        layout.addWidget(self.assign_drone_combo)
        layout.addWidget(self.update_target_button)
        layout.addWidget(self.delete_target_button)
        self.target_tab.setLayout(layout)

    def add_random_target(self):
        target_id = f"Hedef {len(self.targets) + 1}"
        position = (random.randint(0, 100), random.randint(0, 100))
        assigned_drone = random.choice(["Drone 1", "Drone 2"])
        target = {"ad": target_id, "konum": position, "drone": assigned_drone}
        self.targets.append(target)
        self.update_target_list()

    def remove_last_target(self):
        if self.targets:
            self.targets.pop()
            self.update_target_list()

    def update_target_list(self):
        self.target_list.clear()
        for target in self.targets:
            self.target_list.addItem(
                f"{target['ad']} - Konum: {target['konum']} - Drone: {target['drone']}"
            )

    def update_drone_data(self):
        for drone in self.drone_data:
            drone["konum"] = (random.randint(0, 100), random.randint(0, 100))
            drone["hız"] = random.uniform(0, 10)
            drone["yükseklik"] = random.randint(0, 100)
            drone["yaw"] = random.uniform(0, 360)
            drone["pitch"] = random.uniform(-90, 90)
            drone["roll"] = random.uniform(-90, 90)

        drone_info = "".join(
            [
                f"Drone {i + 1}: Konum={drone['konum']}, Hız={drone['hız']:.2f}, Yükseklik={drone['yükseklik']}\n"
                for i, drone in enumerate(self.drone_data)
            ]
        )
        self.drone_info_label.setText(drone_info)

    def update_target_assignment(self):
        current_item = self.target_list.currentRow()
        if current_item >= 0:
            new_drone = self.assign_drone_combo.currentText()
            self.targets[current_item]["drone"] = new_drone
            self.update_target_list()

    def delete_selected_target(self):
        current_item = self.target_list.currentRow()
        if current_item >= 0:
            del self.targets[current_item]
            self.update_target_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Karanlık tema
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1E1E1E"))
    palette.setColor(QPalette.WindowText, QColor("#D4D4D4"))
    palette.setColor(QPalette.Base, QColor("#2D2D30"))
    palette.setColor(QPalette.AlternateBase, QColor("#3E3E42"))
    palette.setColor(QPalette.ToolTipBase, QColor("#D4D4D4"))
    palette.setColor(QPalette.ToolTipText, QColor("#1E1E1E"))
    palette.setColor(QPalette.Text, QColor("#D4D4D4"))
    palette.setColor(QPalette.Button, QColor("#3E3E42"))
    palette.setColor(QPalette.ButtonText, QColor("#D4D4D4"))
    palette.setColor(QPalette.BrightText, QColor("#FF0000"))
    palette.setColor(QPalette.Highlight, QColor("#007ACC"))
    palette.setColor(QPalette.HighlightedText, QColor("#1E1E1E"))
    app.setPalette(palette)

    window = DroneApp()
    window.setPalette(palette)  # Apply palette to the main window
    window.show()
    sys.exit(app.exec_())
