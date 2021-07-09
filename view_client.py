'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-09 08:19:31
 # @ Modified time: 2021-07-09 08:26:36
 # @ Description:
 '''

from ctypes.wintypes import WORD
import sys

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication, QBoxLayout, QComboBox, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QGridLayout, QPushButton, QSizePolicy, QSpacerItem, QStyleFactory, QTabWidget, QTextBrowser, QVBoxLayout, QWidget

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

from QLed import QLed

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

class View(QWidget):
    def __init__(self,name):
        super().__init__()
        self.layout = QGridLayout(self)
        self.tabs = QTabWidget()
        self.tabControl = QWidget()
        self.tabSetup = QWidget()
        
        # Add tabs
        self.tabs.addTab(self.tabControl,"Control")
        self.tabs.addTab(self.tabSetup,"Setup")
        

        # Create first tab
        self.createControlBox()
        self.createPositionDisplay()
        self.createConsoleOutput()

        controlOuterLayout = QVBoxLayout()
        self.tabControl.setLayout(controlOuterLayout)
        
        controlTopLeftLayout = QVBoxLayout()
        controlTopLeftLayout.addWidget(self.controlBox)
        controlTopLeftLayout.addStretch(1)

        controlTopLayout = QHBoxLayout()
        controlTopLayout.addLayout(controlTopLeftLayout)
        controlTopLayout.addWidget(self.positionDisplay)

        controlOuterLayout.addLayout(controlTopLayout)
        controlOuterLayout.addWidget(self.consoleOutput)

        # Create second tab
        sampleTimeSeconds = {"2":2,"5":5,"7":7,"10":10,"15":15,"20":20,"30":30,"60":60}
        sampleComboBox = QComboBox()
        sampleComboBox.addItems(sampleTimeSeconds.keys())
        sampleLabel = QLabel("&Sample rate [s]:")
        sampleLabel.setBuddy(sampleComboBox)

        dataFormats = [".csv", ".xlsx", ".txt"]
        dataFormatBox = QComboBox()
        dataFormatBox.addItems(dataFormats)
        dataFormatLabel = QLabel("&Format:")
        dataFormatLabel.setBuddy(dataFormatBox)

        
        setupTopBox = QGroupBox("Measurement setings")
        setupTopLayout = QVBoxLayout()
        setupTopLayout.addWidget(sampleLabel)
        setupTopLayout.addWidget(sampleComboBox)
        setupTopBox.setLayout(setupTopLayout)

        setupOuterLayout = QVBoxLayout()
        setupOuterLayout.addWidget(setupTopBox)
        self.tabSetup.setLayout(setupOuterLayout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def createControlBox(self):
        self.controlBox = QGroupBox("Control and Status")
        startButton = QPushButton("START")
        stopButton = QPushButton("STOP")

        uartDesc = QLabel(self)
        uartDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        uartDesc.setText("UART:")
        psdDesc = QLabel(self)
        psdDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        psdDesc.setText("PSD:")
        measDesc = QLabel(self)
        measDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        measDesc.setText("MEAS:")

        uartLed = QLed(self, onColour=QLed.Green, shape=QLed.Circle)
        psdLed = QLed(self, onColour=QLed.Green, shape=QLed.Circle)
        measLed = QLed(self, onColour=QLed.Green, shape=QLed.Circle)

        timeDesc = QLabel(self)
        timeDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        timeDesc.setText("Ending measurements in:")
        timeText = QLabel(self)
        timeText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        timeText.setText("<b>09:10:10</b>")

        layout = QGridLayout()
        layout.addWidget(startButton,0,0,1,3)
        layout.addWidget(stopButton,0,3,1,3)
        layout.addWidget(uartDesc,1,0,1,2)
        layout.addWidget(uartLed,2,0,1,2)
        layout.addWidget(psdDesc,1,2,1,2)
        layout.addWidget(psdLed,2,2,1,2)
        layout.addWidget(measDesc,1,4,1,2)
        layout.addWidget(measLed,2,4,1,2)
        layout.addWidget(timeDesc,3,0,1,6)
        layout.addWidget(timeText,4,0,1,6)

        # layout = QVBoxLayout()
        # layout.addWidget(startButton)
        # layout.addWidget(stopButton)
        # layout.addWidget(uartText)
        # layout.addWidget(uartLed)
        # layout.addWidget(psdText)
        # layout.addWidget(psdLed)
        # layout.addWidget(measText)
        # layout.addWidget(measLed)
        # layout.addStretch()

        self.controlBox.setLayout(layout)

    def createPositionDisplay(self):
        self.positionDisplay = QGroupBox("Position")
        plot = AspectRatioWidget(pg.PlotWidget(),self.positionDisplay)
        layout = QGridLayout()
        layout.addWidget(plot,0,0)
        self.positionDisplay.setLayout(layout)

    def createConsoleOutput(self):
        self.consoleOutput = QGroupBox("Console Output")
        out = QTextBrowser()
        out.append("Test")
        layout = QGridLayout()
        layout.addWidget(out,0,0)
        self.consoleOutput.setLayout(layout)


class AspectRatioWidget(QWidget):
    def __init__(self, widget, parent):
        super().__init__(parent)
        self.aspect_ratio = 1
        layout = QBoxLayout(QBoxLayout.LeftToRight, self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        #  add widget, then spacer
        self.layout().addWidget(widget)
        self.layout().addItem(QSpacerItem(0, 0))

    def resizeEvent(self, e):
        w = e.size().width()
        h = e.size().height()
        if w / h > self.aspect_ratio:  # too wide
            self.layout().setDirection(QBoxLayout.LeftToRight)
            widget_stretch = h * self.aspect_ratio
            outer_stretch = (w - widget_stretch) - 1
        else:  # too tall
            self.layout().setDirection(QBoxLayout.TopToBottom)
            widget_stretch = w / self.aspect_ratio
            outer_stretch = (h - widget_stretch) - 1 

        self.layout().setStretch(0, widget_stretch)
        self.layout().setStretch(1, outer_stretch)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())