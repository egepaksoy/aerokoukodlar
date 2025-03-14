import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from saldiri import Ui_MainWindow_Saldiri
from tespit import Ui_MainWindow_Tespit
from hedefler import Ui_MainWindow as Ui_Hedefler


class SaldiriEkrani(QMainWindow, Ui_MainWindow_Saldiri):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.ac_hedef_ekrani)

    def ac_hedef_ekrani(self):
        self.hedef_ekrani = HedefEkrani()
        self.hedef_ekrani.show()


class TespitEkrani(QMainWindow, Ui_MainWindow_Tespit):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.ac_hedef_ekrani)

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
    tespit_ekrani = TespitEkrani()
    
    saldiri_ekrani.show()
    tespit_ekrani.show()
    
    sys.exit(app.exec())
