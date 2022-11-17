from PyQt5.QtWidgets import QApplication
from Classes.GUI.MainWindow import MainWindow




class UIController:
    def __init__(self):
        app = QApplication([])

        window = MainWindow()
        window.show()
        app.exec_()
        pass



