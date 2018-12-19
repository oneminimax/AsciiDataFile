import numpy as np
from os import path
import time
import re

class Writer(object):
    def __init__(self,fileName,autoNumbering = True,separator = ','):
        self.fileName = fileName
        self.autoNumbering = autoNumbering
        self.separator = separator

        self._openFile()

    def _openFile(self):

        if self.autoNumbering:
            self.checkExistingFile()

        self.fId = open(self.fileName,'w')

    def close(self):

        self.fId.close()

    def checkExistingFile(self):

        newFileName = self.fileName
        while path.isfile(newFileName):
            m = re.match('(.+)_(\d{3}).([^.]+)\Z',newFileName)
            if m:
                baseName = m.group(1)
                dig = int(m.group(2))
                ext = m.group(3)
                newFileName = '{0:s}_{1:03d}.{2:s}'.format(baseName,dig+1,ext)
            else:
                root, ext = path.splitext(newFileName)
                newFileName = root + '_002' + ext

        print(self.fileName,'-->',newFileName)

        self.fileName = newFileName

    def writeData(self,dataArray):

        for i in range(dataArray.shape[0]):
            self.addDataPoint(dataArray[i])

    def addDataPoint(self,newData):

        lineStr = ''
        for j in range(len(newData)):
            lineStr += "{0:+10.8e}{1:s}".format(newData[j],self.separator)

        if lineStr:
            self.fId.write(lineStr[:-len(self.separator)] + "\n")
            self.fId.flush()

class MDDataFileWriter(Writer):
    
    def writeHeader(self,nameList,unitList = list()):

        self.fId.write("{0:s}\n".format(time.strftime("%c")))
        self.fId.write("[Header]\n")
        if len(unitList) > 0:
            for i, fieldName in enumerate(nameList):
                self.fId.write("Column {0:2d} : {1:20s}\t{2:s}\n".format(i, fieldName, unitList[i]))
        else:
            for i, fieldName in enumerate(nameList):
                self.fId.write("Column {0:2d} : {1:20s}\n".format(i, fieldName))

        self.fId.write("[Header end]\n\n")
        self.fId.flush()

    def writeDataContainer(self,DC):

        self.writeHeader(DC.fieldNameList,DC.unitList)

        self.writeData(DC.dataArray)

