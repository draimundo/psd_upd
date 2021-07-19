'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-14 07:47:05
 # @ Modified time: 2021-07-15 08:19:25
 # @ Description:
 '''

from datetime import datetime
import os.path

from PySide6 import QtGui
from PySide6 import QtWidgets
from export_client import exportClientCsv, exportClientXlsx
from meas_client import MeasWorkerPlotSignal, MeasWorker, MeasWorkerTextSignal
from numpy import double
from serial_client import Serial_client

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QComboBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QGridLayout, QPushButton, QSpinBox, QTextBrowser, QVBoxLayout, QWidget

from pyqtgraph.Qt import QtCore
import pyqtgraph as pg

class View(QWidget):
    def __init__(self,name):
        super().__init__()

        self.generateLayout()

        self.startButton.clicked.connect(self.startMeas)
        self.stopButton.clicked.connect(self.stopMeas)

        self.exportClient = None
        self.serial = Serial_client()
        self.threadpool = QtCore.QThreadPool()
        self.textSignal = MeasWorkerTextSignal()
        self.plotSignal = MeasWorkerPlotSignal()
        self.textSignal.result.connect(self.appendLineToConsole)
        self.plotSignal.result.connect(self.addToPlot)

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
        
        self.initExportClient()

        self.sampleTimer.timeout.connect(self.getMeas)
        self.sampleTimer.start(self.sampleRateBox.value()*1000) #TODO race condition

        self.measTimer.timeout.connect(self.stopMeas)
        self.measTimer.start(self.measTimeBox.value()*60*1000)

        self.displayTimer.timeout.connect(self.updateTimeField)
        self.displayTimer.start(50)

        
    def initExportClient(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        #fileName, _ = QFileDialog.getSaveFileName(self,"Save File",datetime.now().strftime("%Y-%m-%d_%H%M%S"),"All Files (*);;Excel Files (*.xlsx);;Comma-Separated-Values (*.csv)", options=options)
        
        dialog = QtWidgets.QFileDialog()
        dialog.setOptions(QFileDialog.DontUseNativeDialog)
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.selectFile(datetime.now().strftime("%Y%m%d_%H%M%S-PSDMeas") + self.dataFormatBox.currentText())
        dialog.setDefaultSuffix(self.dataFormatBox.currentText())
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setNameFilters(['Comma-Separated Values (*.csv)', 'Excel Files (*.xlsx)'])
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            fileName = dialog.selectedFiles()[0]
            extension = os.path.splitext(fileName)[1]
            if(extension == ".xlsx"):
                self.exportClient = exportClientXlsx()
            elif(extension == ".csv"):
                self.exportClient = exportClientCsv()
            else:
                self.appendLineToConsole("Extension not supported. Data will not be exported.")
                return
            self.appendLineToConsole("Writing data to {:s} .".format(str(fileName)))
            self.exportClient.init(fileName)
            self.exportClient.writeRow(["Measurement date: {:s}".format(datetime.now().strftime("%Y/%m/%d"))])
            self.exportClient.writeRow(["Sampling rate: {:d} second(s) between measurements".format(self.sampleRateBox.value())])
            self.exportClient.writeRow(["Deviation from the optimal 90° tracker angle"])
            self.exportClient.writeRow(["Local Time","x+","y+","x-","y-","x-position [mm]", "y-position [mm]", "x-deviation [deg]", "y-deviation [deg]"])
        else:
            self.appendLineToConsole("Operation cancelled. Data will not be exported.")

    def updateTimeField(self):
        rem = self.measTimer.remainingTime()
        min,sec = divmod(rem/1000,60)
        self.timeText.setText('<b>{:g}:{:.1f}<\b>'.format(min,sec))

    def getMeas(self):
        measWorker = MeasWorker(uartHandle=self.serial, exportHandle=self.exportClient, plotSignal=self.plotSignal, textSignal=self.textSignal)
        self.threadpool.start(measWorker)

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
        self.sampleTimer.timeout.disconnect()
        self.sampleTimer.stop()
        self.serial.close()

        self.measTimer.timeout.disconnect()
        self.measTimer.stop()
        
        self.displayTimer.timeout.disconnect()
        self.displayTimer.stop()
        self.timeText.setText('<b>-<\b>')

        self.startButton.setDisabled(False)
        self.stopButton.setEnabled(False)
        self.setupBox.setDisabled(False)

        self.ledColor(self.measLed,False)
        self.ledColor(self.uartLed,False)
        self.ledColor(self.psdLed,False)
        
        self.appendLineToConsole("- - - - - - - - - - - - -")
        if(self.exportClient != None):
            self.exportClient.close()


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

        self.displayTimer = QTimer(self)
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
        self.plot.showGrid(x=True, y=True)
        self.plot.setXRange(-10,10)
        self.plot.setYRange(-10,10)
        layout = QGridLayout()
        layout.addWidget(self.plot,0,0)

        self.scatterItem = pg.ScatterPlotItem()
        self.plot.addItem(self.scatterItem)

        self.positionDisplayBox = QGroupBox("Position")
        self.positionDisplayBox.setLayout(layout)
        self.plotInit = False

    @QtCore.Slot(float,float)
    def addToPlot(self,x,y):
        self.scatterItem.setData(x=[x],y=[y])

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

        dataFormats = [".csv", ".xlsx"]
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
        #setupLayout.addWidget(dataFormatLabel,2,0)
        #setupLayout.addWidget(self.dataFormatBox,2,1)
        setupLayout.addWidget(comSelectLabel,3,0)
        setupLayout.addWidget(self.comSelectBox,3,1)

        self.setupBox = QGroupBox("Measurement setings")
        self.setupBox.setLayout(setupLayout)