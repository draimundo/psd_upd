'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-09 08:19:23
 # @ Modified time: 2021-07-09 08:26:31
 # @ Description:
 '''

from numpy import exp
import serial
import serial.tools.list_ports

class Serial_client():
  def __init__(self):
      self.serial_client = serial.Serial()

  def open(self,port):
    self.serial_client.port = port
    self.serial_client.baudrate = 9600
    self.serial_client.bytesize = serial.EIGHTBITS
    self.serial_client.stopbits = serial.STOPBITS_ONE
    self.serial_client.write_timeout = 1
    self.serial_client.timeout = 1

    try:
      self.serial_client.open()
      ret = self.serial_client.port + " successfully opened."
    except Exception as ex:
      ret = str(ex)
    return ret

  def close(self):
    try:
      self.serial_client.reset_input_buffer()
      self.serial_client.reset_output_buffer()
      self.serial_client.close()
      ret = self.serial_client.port + " closed."
    except Exception as ex:
      ret = str(ex)
    return ret

  def write(self,data):
    try:
      ret = self.serial_client.write(data)
      # self.serial_client.flush()
    except Exception as ex:
      ret = str(ex)
    return ret

  def readLine(self):
    try:
      ret = self.serial_client.read_until(expected=b"\0")
      ret = ret[:-1].decode('ascii') #remove eol
    except Exception as ex:
      ret = str(ex)
    return ret

  def writeread(self,data):
    self.write(data)
    return self.readLine()

  def listPorts(self):
    b = []
    for a in list(serial.tools.list_ports.comports()):
      b.append(a.device)
    #print(b)
    return b

if __name__ == "__main__":
    a = Serial_client()
    a.open(a.listPorts()[0])
    a.readLine()