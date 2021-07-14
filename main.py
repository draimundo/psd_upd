'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-09 08:19:31
 # @ Modified time: 2021-07-09 08:26:36
 # @ Description:
 '''

import sys
from view_client import View

from PySide6.QtWidgets import QApplication, QMainWindow, QStyleFactory


class Main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = Window()   

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.setGeometry(0,0,724,839)
        #self.showMaximized()
        self.setWindowTitle("PSD_Viewer")

        self.view = View(self)
        self.setCentralWidget(self.view)

        QApplication.setStyle(QStyleFactory.create('windowsvista'))

        self.show()


if __name__ == "__main__":
    main = Main()

    sys.exit(main.app.exec())