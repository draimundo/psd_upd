'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-14 07:47:05
 # @ Modified time: 2021-07-14 07:47:17
 # @ Description:
 '''

from datetime import datetime
from meas_client import MeasWorkerSignals, MeasWorker
from numpy import double
from serial_client import Serial_client

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QGridLayout, QPushButton, QSpinBox, QTextBrowser, QVBoxLayout, QWidget

from pyqtgraph.Qt import QtCore
import pyqtgraph as pg

class View(QWidget):
    def __init__(self,name):
        super().__init__()

        self.generateLayout()

        self.startButton.clicked.connect(self.startMeas)
        self.stopButton.clicked.connect(self.stopMeas)

        self.serial = Serial_client()
        self.threadpool = QtCore.QThreadPool()
        self.measSignal = MeasWorkerSignals()
        self.measSignal.result.connect(self.appendLineToConsole)

        self.comSelectBox.removeItem(0)
        self.comSelectBox.addItems(self.serial.listPorts())
    
    def generateLayout(self):
        self.layout = QHBoxLayout(self)

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

        self.layout.addLayout(outerLayout)
        self.setLayout(self.layout)

    def startMeas(self):
        self.startButton.setDisabled(True)
        self.stopButton.setEnabled(True)
        self.setupBox.setDisabled(True)

        #self.out.clear()
        self.appendLineToConsole(self.serial.open(self.comSelectBox.currentText()))
        self.ledColor(self.uartLed,True)

        self.psdReady()
        self.measReady()
        self.measRunning()

        self.sampleTimer.setInterval(self.sampleRateBox.value()*1000)
        ret = self.sampleTimer.interval()
        self.measTimer.setInterval(self.measTimeBox.value()*1000)

        measWorker = MeasWorker(uartHandle=self.serial, signals=self.measSignal)
        QtCore.QObject.connect(self.sampleTimer, QtCore.SIGNAL("timeout()"), measWorker.run())
        self.sampleTimer.start()

    def psdReady(self):
        ret = self.serial.writeread(b"a")
        if(ret == "PSD ist bereit"):
            self.ledColor(self.psdLed,True)
            self.appendLineToConsole("PSD is ready")
            # TODO PSD not ready... 


    def measReady(self):
        ret = self.serial.writeread(b"b")
        if(ret == "bereit zum messen"):
            self.appendLineToConsole("Ready to measure")
            #Meas not ready... TODO

    def measRunning(self):
        ret = self.serial.writeread(b"c")
        if(ret == "Messungen laufen"):
            self.ledColor(self.measLed,True)
            self.appendLineToConsole("Measuring...")
            #Meas not ready... TODO

    def stopMeas(self):
        self.startButton.setDisabled(False)
        self.stopButton.setEnabled(False)
        self.setupBox.setDisabled(False)

        self.ledColor(self.measLed,False)
        self.ledColor(self.uartLed,False)
        self.ledColor(self.psdLed,False)
        self.serial.close()
        self.appendLineToConsole("- - - - - - - - - - - - -")

    def ledColor(self,led,status):
        if status:
            led.setStyleSheet("background-color:green")
        else:
            led.setStyleSheet("background-color:red")

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
        self.ledColor(self.uartLed,False)
        self.psdLed = QPushButton()
        self.psdLed.setDisabled(True)
        self.ledColor(self.psdLed,False)
        self.measLed = QPushButton()
        self.measLed.setDisabled(True)
        self.ledColor(self.measLed,False)

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
        layout = QGridLayout()
        layout.addWidget(self.out,0,0)
        self.consoleOutputBox.setLayout(layout)

    @QtCore.Slot(str)
    def appendLineToConsole(self,text):
        self.out.append(datetime.now().strftime("[%H:%M:%S] ") + str(text))

    def createSetupBox(self):
        self.sampleRateBox = QSpinBox()
        self.sampleRateBox.setMinimum(1)
        self.sampleRateBox.setMaximum(60)
        self.sampleTimer = QTimer(self)
        sampleLabel = QLabel("&Sample rate [s]:")
        sampleLabel.setBuddy(self.sampleRateBox)

        self.measTimeBox = QSpinBox()
        self.measTimeBox.setMinimum(1)
        self.measTimeBox.setValue(60)
        self.measTimeBox.setMaximum(14400)
        self.measTimer = QTimer(self)
        measTimeLabel = QLabel("&Meas. time [min]:")
        measTimeLabel.setBuddy(self.measTimeBox)

        dataFormats = [".csv", ".txt", ".xlsx"]
        self.dataFormatBox = QComboBox()
        self.dataFormatBox.addItems(dataFormats)
        dataFormatLabel = QLabel("&Export format:")
        dataFormatLabel.setBuddy(self.dataFormatBox)
        
        comPorts = ["not. init"]
        self.comSelectBox = QComboBox()
        self.comSelectBox.addItems(comPorts)
        comSelectLabel = QLabel("COM port:")
        comSelectLabel.setBuddy(self.comSelectBox)

        setupLayout = QGridLayout()
        setupLayout.addWidget(sampleLabel,0,0)
        setupLayout.addWidget(self.sampleRateBox,0,1)
        setupLayout.addWidget(measTimeLabel,1,0)
        setupLayout.addWidget(self.measTimeBox,1,1)
        setupLayout.addWidget(dataFormatLabel,2,0)
        setupLayout.addWidget(self.dataFormatBox,2,1)
        setupLayout.addWidget(comSelectLabel,3,0)
        setupLayout.addWidget(self.comSelectBox,3,1)

        self.setupBox = QGroupBox("Measurement setings")
        self.setupBox.setLayout(setupLayout)