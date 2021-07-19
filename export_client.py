'''
 # @ Author: Daniel Raimundo (DR)
 # @ Create Time: 2021-07-09 08:19:37
 # @ Modified time: 2021-07-09 08:26:22
 # @ Description:
 '''

import xlsxwriter
import csv

class exportClientXlsx:
    def init(self,filename):
        self.filename = filename
        self.workbook = xlsxwriter.Workbook('{:s}'.format(filename))
        self.worksheet = self.workbook.add_worksheet()
        self.row = 0

    def writeRow(self,writeList):
        for col, data in enumerate(writeList):
            self.worksheet.write(self.row,col,data)
        self.row += 1

    def close(self):
        self.workbook.close()

class exportClientCsv:
    def init(self,filename):
        self.filename = filename
        self.csvFile = open('{:s}'.format(filename), mode='w', newline='')
        self.writer = csv.writer(self.csvFile)
    
    def writeRow(self,writeList):
        self.writer.writerow(writeList)

    def close(self):
        self.csvFile.close()