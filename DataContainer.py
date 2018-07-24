import numpy as np

class DataContainer(object):
    chunkSize = 3
    def __init__(self,nameList = list(),unitList = list(),numberOfDataField = 0):

        if len(nameList) > 0:
            self.numberOfDataField = len(nameList)
            self.nameList = nameList
        elif len(unitList) > 0:
            self.numberOfDataField = len(unitList)
            self.nameList = self._genericDataFieldNameList()
        elif numberOfDataField > 0:
            self.numberOfDataField = numberOfDataField
            self.nameList = self._genericDataFieldNameList()

        if len(unitList) == self.numberOfDataField:
            self.unitList = unitList
        else:
            self.unitList = self._genericUnitList()

        self.dataArray = np.empty((self.chunkSize,self.numberOfDataField))
        self.numberOfDataPoint = 0

    def __str__(self):

        string = ''
        for fieldName in self.nameList:
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

        nameList = list()
        for i in range(self.numberOfDataField):
            nameList.append('Data Field {0:d}'.format(i+1))

        return nameList

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

    def getField(self,index):

        return self.dataArray[:self.numberOfDataPoint,index]