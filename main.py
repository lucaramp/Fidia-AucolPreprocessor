from PySide2.QtWidgets import QApplication
from MainWindow import MainWindow


if __name__ == "__main__":
    print("Starting....")
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
