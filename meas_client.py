'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-14 07:50:42
 # @ Modified time: 2021-07-14 07:52:25
 # @ Description:
 '''

from PySide6 import QtCore
import numpy
from numpy import double


class MeasWorkerSignals(QtCore.QObject):
    result = QtCore.Signal(str)


class MeasWorker(QtCore.QRunnable):
    def __init__(self, uartHandle, exportHandle, signals):
        super(MeasWorker, self).__init__()
        self.exportHandle = exportHandle
        self.uartHandle = uartHandle
        self.signals = signals

    def run(self):
        self.uartHandle.write(b"d")
        xpos = double(self.uartHandle.readLine())
        ypos = double(self.uartHandle.readLine())
        xneg = double(self.uartHandle.readLine())
        yneg = double(self.uartHandle.readLine())
        temp = double(self.uartHandle.readLine())/10.0

        xposition = (5.7 * ((xpos + yneg) - (xneg + ypos))) / (2 * (xpos + ypos + xneg + yneg))
        xdeviation = numpy.arctan(xposition/67.4)*(180/numpy.pi)

        yposition = (5.7 * ((xpos + ypos) - (xneg + yneg))) / (2 * (xpos + ypos + xneg + yneg))
        ydeviation = numpy.arctan(yposition/67.4)*(180/numpy.pi)

        ret = "Measurements: x+: " + str(xpos) + "; y+: " + str(ypos) + "; x-: " + str(xneg) + "; y-: " + str(yneg) + "; temp: " + str(temp) + "\r\n" + "Measurements: xpos: " + '{:f}'.format(xposition) + "; ypos : " + '{:f}'.format(yposition) + "; xdev: " + '{:f}'.format(xdeviation) + "; ydev: " + '{:f}'.format(ydeviation)
        
        self.exportHandle.writeRow([str(xpos), str(ypos), str(xneg), str(yneg), str(xposition), str(yposition), str(xdeviation), str(ydeviation)])

        self.signals.result.emit(ret)