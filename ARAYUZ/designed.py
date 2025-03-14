from PyQt6.QtWidgets import QApplication, QMainWindow
from saldiri import Ui_MainWindow_Saldiri
from tespit import Ui_MainWindow_Tespit
import sys

class SaldiriApp(QMainWindow, Ui_MainWindow_Saldiri):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class TespitApp(QMainWindow, Ui_MainWindow_Tespit):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

app = QApplication(sys.argv)

saldiri_window = SaldiriApp()
saldiri_window.show()

tespit_window = TespitApp()
tespit_window.show()

sys.exit(app.exec())