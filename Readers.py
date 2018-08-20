import numpy as np
import re

class Reader(object):

    def __init__(self):

        pass

    def read(self,filePath):

        self._openFile(filePath)
        self._readHeader()

        self.fieldNameList, self.unitList, self.columnNumber = self.defineFieldUnitColumn()
        self._initDataInterpret()
        
        DC = self._readData()

        return DC
    
    def __str__(self):

        return str(self.getFieldNameList())

    def _openFile(self,filePath):
        try:
            self.fId = open(filePath,'r')

        except IOError:
            print("Cannot open {0:s}".format(filePath))
            raise

    def _readHeader(self):

        pass

    def _readLine(self):

        return self.fId.readline()

    def _lineMatch(self,line,patern):

        return bool(re.match(patern,line))

    def _newDataContainer(self):
        
        return DataContainer(fieldNameList = self.fieldNameList,unitList = self.unitList)

    def _initDataInterpret(self):

        fieldColumnDict = dict()
        for i, fieldName in enumerate(self.fieldNameList):
            fieldColumnDict[fieldName] = self.columnNumber[i]

        self.fieldColumnDict = fieldColumnDict

    def _readDataLine(self):

        line = self._readLine()
        splitedLine = re.split(self.separator,line)
        if len(splitedLine) >= len(self.fieldNameList):
            newData = self.interpretDataLine(splitedLine)
        else:
            newData = None
        
        return bool(line), newData

    def interpretDataLine(self,splitedLine):

        newData = np.zeros((len(self.fieldNameList),))
        for iColumn, channel in enumerate(self.fieldNameList):
            columnNumber = self.fieldColumnDict[channel]
            try:
                newData[iColumn] = float(splitedLine[columnNumber])
            except:
                pass

        return newData

        # self.dataContainer

    def _readData(self):

        DC = self._newDataContainer()
    
        while True:
            keepReading, newData = self._readDataLine()
            if keepReading:
                DC.addDataPoint(newData)
            else:
                break

        return DC



class GenericDataReader(Reader):
    def __init__(self,separator,fieldNameList,unitList = list(),nbHeadLine = 0):
        
        self.separator = separator
        self._fieldNameList = fieldNameList
        self._unitList = unitList
        self._nbHeadLine = nbHeadLine

        Reader.__init__(self)

    def defineFieldUnitColumn(self):

        return self._fieldNameList, self._unitList, list(range(len(self._fieldNameList)))

    def _readHeader(self):
        headerLines = list()

        for n in range(self._nbHeadLine):
            headerLines.append(self.fId.readline())

class MDDataFileReader(Reader):
    separator = ','

    def _readHeader(self):

        headerLines = list()

        while True:
            line = self.fId.readline()
            if not line:
                break
            m1 = re.match("\[Header\]",line)
            m2 = re.match("\[Instrument List\]",line)
            if m1 or m2:
                break

        while True:
            line = self.fId.readline()
            if not line:
                break
            m1 = re.match("\[Header end\]",line)
            m2 = re.match("\[Instrument List end\]",line)
            if m1 or m2:
                break
            else:
                headerLines.append(line.strip())

        fieldNameList = list()
        unitList = list()
        for line in headerLines:
            m = re.match("Column .. : (.+)",line)
            if m:
                subLine = m.group(1)
                m1 = re.match("([\w -]+)\t(.+)$",subLine)
                m2 = re.match("([\w -]+) in (\w+)",subLine)
                if m2:
                    m22 = re.match("(.+)\s+(\w+)\s+(\w+)$",m2.group(1).strip())
                    fieldNameList.append(m22.group(2).strip())
                    unitList.append(m2.group(2).strip())
                elif m1:
                    fieldNameList.append(m1.group(1).strip())
                    unitList.append(m1.group(2).strip())
                else:
                    fieldNameList.append(subLine.strip())
                    unitList.append('u.a.')

        self._fieldNameList = fieldNameList
        self._unitList = unitList

    def defineFieldUnitColumn(self):

        return self._fieldNameList, self._unitList, list(range(len(self._fieldNameList)))

class SQUIDDataReader(Reader):

    separator = ','

    def _readHeader(self):

        while True:
            line = self._readLine()
            if self._lineMatch(line,"\[Data\]"):
                break

    def defineFieldUnitColumn(self):

        fieldNameList = [
            'time',
            'magnetic field',
            'temperature',
            'long moment',
            'long scan std dev',
            'long algorithm',
            'long reg fit',
            'long percent error'
            ]
        fieldUnitList = [
            's',
            'Oe',
            'K',
            'emu',
            'emu',
            None,
            None,
            '%'
            ]
        columnNumber = [0,2,3,4,5,6,7,8]

        return fieldNameList, fieldUnitList, columnNumber

class PPMSResistivityDataReader(Reader):

    separator = ','

    def __init__(self,sampleNumber = 0):
        self.sampleNumber = sampleNumber
        Reader.__init__(self)
        

    def _readHeader(self):

        while True:
            line = self._readLine()
            if self._lineMatch(line,"\[Data\]"):
                break
        line = self._readLine()

    def defineFieldUnitColumn(self):

        fieldNameList = [
            'time',
            'temperature',
            'magnetic field',
            'sample position'
            ]
        fieldUnitList = [
            's',
            'K',
            'Oe',
            'deg',
            ]
        columnNumber = [1,3,4,5]

        if self.sampleNumber == 0:
            for i in range(1,4):
                fieldNameList.append('resistance{0:d}'.format(i))
                fieldUnitList.append('ohm')
                columnNumber.append(4 + 2*i)
                fieldNameList.append('current{0:d}'.format(i))
                fieldUnitList.append('uA')
                columnNumber.append(5 + 2*i)

        elif self.sampleNumber in [1,2,3]:
            fieldNameList.append('resistance')
            fieldUnitList.append('ohm')
            columnNumber.append(4 + 2*self.sampleNumber)
            fieldNameList.append('current')
            fieldUnitList.append('uA')
            columnNumber.append(5 + 2*self.sampleNumber)

        return fieldNameList, fieldUnitList, columnNumber

class PPMSACMSDataReader(Reader):

    separator = ','

    def __init__(self,numberOfHarmonics = 1):

        self.numberOfHarmonics = numberOfHarmonics

        Reader.__init__(self)
        

    def _readHeader(self):

        while True:
            line = self._readLine()
            if self._lineMatch(line,"\[Data\]"):
                break
        line = self._readLine()

    def defineFieldUnitColumn(self):

        fieldNameList = [
            'time',
            'temperature',
            'magnetic field',
            'frequency',
            'amplitude',
            'magnetization dc',
            'magnetization std'
            ]
        fieldUnitList = [
            's',
            'K',
            'Oe',
            'Hz',
            'Oe',
            'emu',
            'emu'
            ]
        columnNumber = [1,2,3,4,5,6,7]

        for har in range(self.numberOfHarmonics):
            fieldNameList.append("magnetizationReal[{0:d}]".format(har+1))
            fieldUnitList.append('')
            columnNumber.append(8 + 4 * har)
            fieldNameList.append("magnetizationImag[{0:d}]".format(har+1))
            fieldUnitList.append('')
            columnNumber.append(9 + 4 * har)
            fieldNameList.append("magnetizationAbs[{0:d}]".format(har+1))
            fieldUnitList.append('')
            columnNumber.append(10 + 4 * har)
            fieldNameList.append("magnetizationPhase[{0:d}]".format(har+1))
            fieldUnitList.append('')
            columnNumber.append(11 + 4 * har)

        return fieldNameList, fieldUnitList, columnNumber

class DataContainer(object):
    chunkSize = 3
    def __init__(self,fieldNameList = list(),unitList = list(),numberOfDataField = 0):

        if len(fieldNameList) > 0:
            self.numberOfDataField = len(fieldNameList)
            self.fieldNameList = fieldNameList
        elif len(unitList) > 0:
            self.numberOfDataField = len(unitList)
            self.fieldNameList = self._genericDataFieldNameList()
        elif numberOfDataField > 0:
            self.numberOfDataField = numberOfDataField
            self.fieldNameList = self._genericDataFieldNameList()

        if len(unitList) == self.numberOfDataField:
            self.unitList = unitList
        else:
            self.unitList = self._genericUnitList()

        self.dataArray = np.empty((self.chunkSize,self.numberOfDataField))
        self.numberOfDataPoint = 0

    def __str__(self):

        string = ''
        for fieldName in self.fieldNameList:
            string += fieldName + "\n"
        string += "number of data point = {0:d}".format(self.numberOfDataPoint)

        return string

    def addDataPoint(self,newData):

        if len(newData) == self.numberOfDataField:
            if self.dataArray.shape[0] == self.numberOfDataPoint:
                self._extendChunk()
            self.dataArray[self.numberOfDataPoint,:] = newData
            self.numberOfDataPoint += 1
        else:
            raise ValueError('New Data Length ({0:d}) is not conform to the number of data fields ({1:d}).'.format(len(newData),self.numberOfDataField))

    def _genericDataFieldNameList(self):

        fieldNameList = list()
        for i in range(self.numberOfDataField):
            fieldNameList.append('Data Field {0:d}'.format(i+1))

        return fieldNameList

    def _genericUnitList(self):
        unitList = list()
        for i in range(self.numberOfDataField):
            unitList.append('a.u.')

        return unitList

    def _extendChunk(self):

        newDataArray = np.empty((self.numberOfDataPoint+self.chunkSize,self.numberOfDataField))
        newDataArray[:self.numberOfDataPoint,:] = self.dataArray
        self.dataArray = newDataArray

    def crop(self):

        newDataArray = np.empty((self.numberOfDataPoint,self.numberOfDataField))
        newDataArray = self.dataArray[:self.numberOfDataPoint,:]
        self.dataArray = newDataArray

    def getArray(self):

        return self.dataArray[:self.numberOfDataPoint,:]

    def getFieldIndex(self,fieldName):

        return self.fieldNameList.index(fieldName)

    def getFieldByIndex(self,index):

        return self.dataArray[:self.numberOfDataPoint,index]

    def getFieldByName(self,fieldName):

        index = self.getFieldIndex(fieldName)
        return self.getFieldByIndex(index)

    def getFieldUnit(self,fieldName):

        index = self.getFieldIndex(fieldName)
        return self.unitList[index]

import numpy as np

class DataContainer(object):
    chunkSize = 3
    def __init__(self,fieldNameList = list(),unitList = list(),numberOfDataField = 0):

        if len(fieldNameList) > 0:
            self.numberOfDataField = len(fieldNameList)
            self.fieldNameList = fieldNameList
        elif len(unitList) > 0:
            self.numberOfDataField = len(unitList)
            self.fieldNameList = self._genericDataFieldNameList()
        elif numberOfDataField > 0:
            self.numberOfDataField = numberOfDataField
            self.fieldNameList = self._genericDataFieldNameList()

        if len(unitList) == self.numberOfDataField:
            self.unitList = unitList
        else:
            self.unitList = self._genericUnitList()

        self.dataArray = np.empty((self.chunkSize,self.numberOfDataField))
        self.numberOfDataPoint = 0

    def __str__(self):

        string = ''
        for fieldName in self.fieldNameList:
            string += fieldName + "\n"
        string += "number of data point = {0:d}".format(self.numberOfDataPoint)

        return string

    def addDataPoint(self,newData):

        if len(newData) == self.numberOfDataField:
            if self.dataArray.shape[0] == self.numberOfDataPoint:
                self._extendChunk()
            self.dataArray[self.numberOfDataPoint,:] = newData
            self.numberOfDataPoint += 1
        else:
            raise ValueError('New Data Length ({0:d}) is not conform to the number of data fields ({1:d}).'.format(len(newData),self.numberOfDataField))

    def _genericDataFieldNameList(self):

        fieldNameList = list()
        for i in range(self.numberOfDataField):
            fieldNameList.append('Data Field {0:d}'.format(i+1))

        return fieldNameList

    def _genericUnitList(self):
        unitList = list()
        for i in range(self.numberOfDataField):
            unitList.append('a.u.')

        return unitList

    def _extendChunk(self):

        newDataArray = np.empty((self.numberOfDataPoint+self.chunkSize,self.numberOfDataField))
        newDataArray[:self.numberOfDataPoint,:] = self.dataArray
        self.dataArray = newDataArray

    def crop(self):

        newDataArray = np.empty((self.numberOfDataPoint,self.numberOfDataField))
        newDataArray = self.dataArray[:self.numberOfDataPoint,:]
        self.dataArray = newDataArray

    def getArray(self):

        return self.dataArray[:self.numberOfDataPoint,:]

    def getFieldIndex(self,fieldName):

        return self.fieldNameList.index(fieldName)

    def getFieldByIndex(self,index):

        return self.dataArray[:self.numberOfDataPoint,index]

    def getFieldByName(self,fieldName):

        index = self.getFieldIndex(fieldName)
        return self.getFieldByIndex(index)

    def getFieldUnit(self,fieldName):

        index = self.getFieldIndex(fieldName)
        return self.unitList[index]


