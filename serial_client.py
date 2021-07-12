'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-09 08:19:23
 # @ Modified time: 2021-07-09 08:26:31
 # @ Description:
 '''

import serial
import serial.tools.list_ports

class Serial_client():
  def __init__(self):
      self.serial = serial.Serial()

def list_ports():
    return list(serial.tools.list_ports.comports())


if __name__ == "__main__":
  inst = Serial_client()
  for a in list_ports():
    print(a)