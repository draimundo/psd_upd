'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-14 07:50:42
 # @ Modified time: 2021-07-14 07:52:25
 # @ Description:
 '''

from datetime import datetime

from numpy import double, arctan, pi
from PySide6 import QtCore
import numpy


class MeasWorkerTextSignal(QtCore.QObject):
    result = QtCore.Signal(str)

class MeasWorkerPlotSignal(QtCore.QObject):
    result = QtCore.Signal(float,float)

class MeasWorker(QtCore.QRunnable):
    def __init__(self, uartHandle, textSignal, plotSignal, exportHandle=None):
        super(MeasWorker, self).__init__()
        self.exportHandle = exportHandle
        self.uartHandle = uartHandle
        self.textSignal = textSignal
        self.plotSignal = plotSignal

    def run(self):
        self.uartHandle.write(b"d")
        try:
            xpos = double(self.uartHandle.readLine())
            ypos = double(self.uartHandle.readLine())
            xneg = double(self.uartHandle.readLine())
            yneg = double(self.uartHandle.readLine())
            temp = double(self.uartHandle.readLine())/10.0
        except ValueError:
            self.textSignal.result.emit("<b>UART port not valid -- RANDOM VALUES as measurements</b>")
            xpos = numpy.random.random_integers(1,5000)
            ypos = numpy.random.random_integers(1,5000)
            xneg = numpy.random.random_integers(1,5000)
            yneg = numpy.random.random_integers(1,5000)
            temp = double(numpy.random.random_integers(1,500))/10.0

        den = 2 * (xpos + ypos + xneg + yneg)

        if(den != 0):
            xposition = (5.7 * ((xpos + yneg) - (xneg + ypos))) / den
            xdeviation = arctan(xposition/67.4)*(180/pi)

            yposition = (5.7 * ((xpos + ypos) - (xneg + yneg))) / den
            ydeviation = arctan(yposition/67.4)*(180/pi)

            text = "Measurements: x+: " + str(xpos) + "; y+: " + str(ypos) + "; x-: " + str(xneg) + "; y-: " + str(yneg) + "; temp: " + str(temp) + "\r\n" + "Measurements: xpos: " + '{:f}'.format(xposition) + "; ypos : " + '{:f}'.format(yposition) + "; xdev: " + '{:f}'.format(xdeviation) + "; ydev: " + '{:f}'.format(ydeviation)
            if(self.exportHandle!=None):
                self.exportHandle.writeRow([datetime.now().strftime("%H:%M:%S.%f")[:-4], str(xpos), str(ypos), str(xneg), str(yneg), str(xposition), str(yposition), str(xdeviation), str(ydeviation), str(temp)])

            self.plotSignal.result.emit(xdeviation, ydeviation)
        else:
            text = "Denominator == 0 = (x+ = " + str(xpos) + " ) + (y+ = " + str(ypos) + " ) + (x- = " + str(xneg) + " ) + (y- = " + str(yneg) + " ); temp: " + str(temp) + "\r\n"
        self.textSignal.result.emit(text)
