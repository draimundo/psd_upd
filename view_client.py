'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-09 08:19:31
 # @ Modified time: 2021-07-09 08:26:36
 # @ Description:
 '''

from ctypes.wintypes import WORD
import sys

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QBoxLayout, QComboBox, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QGridLayout, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QStyleFactory, QTabWidget, QTextBrowser, QVBoxLayout, QWidget

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
        self.layout = QHBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabControl = QWidget()
        self.tabSetup = QWidget()
        
        # Add tabs
        self.tabs.addTab(self.tabControl,"Control")
        self.tabs.addTab(self.tabSetup,"Setup")

        # Create first tab
        self.createControlBox()
        self.createPositionDisplayBox()
        self.createConsoleOutputBox()
        self.createSetupBox()

        controlSetupLayout = QVBoxLayout()
        controlSetupLayout.addWidget(self.controlBox)
        controlSetupLayout.addWidget(self.setupBox)
        controlSetupLayout.addStretch(1)
        
        controlSetupConsoleLayout = QHBoxLayout()
        controlSetupConsoleLayout.addLayout(controlSetupLayout)
        controlSetupConsoleLayout.addWidget(self.consoleOutputBox)
        
        outerLayout = QVBoxLayout()
        outerLayout.addWidget(self.positionDisplayBox, stretch=4)
        outerLayout.addLayout(controlSetupConsoleLayout)

        
        # self.startButton.clicked.connect(self.startButton.setDisabled(True))
        # self.startButton.clicked.connect(self.stopButton.setEnabled(True))

        # self.stopButton.setDisabled(True)
        # self.stopButton.clicked.connect(self.setupBox.setDisabled(False))
        # self.stopButton.clicked.connect(self.stopButton.setDisabled(True))
        # self.stopButton.clicked.connect(self.startButton.setEnabled(True))

        # Add tabs to widget
        self.layout.addLayout(outerLayout)
        self.setLayout(self.layout)

        self.startButton.clicked.connect(self.start_meas)
        self.stopButton.clicked.connect(self.stop_meas)
    
    def start_meas(self):
        self.startButton.setDisabled(True)
        self.stopButton.setEnabled(True)
        self.setupBox.setDisabled(True)

    def stop_meas(self):
        self.startButton.setDisabled(False)
        self.stopButton.setEnabled(False)
        self.setupBox.setDisabled(False)

    def createControlBox(self):
        self.startButton = QPushButton("START")
        self.stopButton = QPushButton("STOP")
        self.stopButton.setDisabled(True)

        uartDesc = QLabel(self)
        uartDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        uartDesc.setText("UART:")
        psdDesc = QLabel(self)
        psdDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        psdDesc.setText("PSD:")
        measDesc = QLabel(self)
        measDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        measDesc.setText("MEAS:")

        self.uartLed = QPushButton()
        self.uartLed.setDisabled(True)
        self.uartLed.setStyleSheet("background-color:red")
        self.psdLed = QPushButton()
        self.psdLed.setDisabled(True)
        self.psdLed.setStyleSheet("background-color:red")
        self.measLed = QPushButton()
        self.measLed.setDisabled(True)
        self.measLed.setStyleSheet("background-color:red")

        timeDesc = QLabel(self)
        timeDesc.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        timeDesc.setText("Ending measurements in:")
        self.timeText = QLabel(self)
        self.timeText.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.timeText.setText("<b>-</b>")

        layout = QGridLayout()
        layout.addWidget(self.startButton,0,0,1,3)
        layout.addWidget(self.stopButton,0,3,1,3)
        layout.addWidget(uartDesc,1,0,1,2)
        layout.addWidget(self.uartLed,2,0,1,2)
        layout.addWidget(psdDesc,1,2,1,2)
        layout.addWidget(self.psdLed,2,2,1,2)
        layout.addWidget(measDesc,1,4,1,2)
        layout.addWidget(self.measLed,2,4,1,2)
        layout.addWidget(timeDesc,3,0,1,6)
        layout.addWidget(self.timeText,4,0,1,6)

        self.controlBox = QGroupBox("Control and Status")
        self.controlBox.setLayout(layout)

    def createPositionDisplayBox(self):
        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked()
        layout = QGridLayout()
        layout.addWidget(self.plot,0,0)

        self.positionDisplayBox = QGroupBox("Position")
        self.positionDisplayBox.setLayout(layout)

    def createConsoleOutputBox(self):
        self.consoleOutputBox = QGroupBox("Console Output")
        self.out = QTextBrowser()
        self.out.append("Test")
        layout = QGridLayout()
        layout.addWidget(self.out,0,0)
        self.consoleOutputBox.setLayout(layout)

    def createSetupBox(self):
        sampleRateBox = QSpinBox()
        sampleRateBox.setMinimum(1)
        sampleRateBox.setMaximum(60)
        sampleLabel = QLabel("&Sample rate [s]:")
        sampleLabel.setBuddy(sampleRateBox)

        measTimeBox = QSpinBox()
        measTimeBox.setMinimum(1)
        measTimeBox.setValue(60)
        measTimeBox.setMaximum(14400)
        measTimeLabel = QLabel("&Meas. time [min]:")
        measTimeLabel.setBuddy(measTimeBox)

        dataFormats = [".csv", ".txt", ".xlsx"]
        dataFormatBox = QComboBox()
        dataFormatBox.addItems(dataFormats)
        dataFormatLabel = QLabel("&Export format:")
        dataFormatLabel.setBuddy(dataFormatBox)
        
        comPorts = ["none"]
        comSelectBox = QComboBox()
        comSelectBox.addItems(comPorts)
        comSelectLabel = QLabel("COM port:")
        comSelectLabel.setBuddy(comSelectBox)

        setupLayout = QGridLayout()
        setupLayout.addWidget(sampleLabel,0,0)
        setupLayout.addWidget(sampleRateBox,0,1)
        setupLayout.addWidget(measTimeLabel,1,0)
        setupLayout.addWidget(measTimeBox,1,1)
        setupLayout.addWidget(dataFormatLabel,2,0)
        setupLayout.addWidget(dataFormatBox,2,1)
        setupLayout.addWidget(comSelectLabel,3,0)
        setupLayout.addWidget(comSelectBox,3,1)

        self.setupBox = QGroupBox("Measurement setings")
        self.setupBox.setLayout(setupLayout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec())