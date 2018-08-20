class HotReader():
    def __init__(self,reader,filePath):

        self.reader = reader
        self.filePath = filePath

        self.dataContainer = reader.read(filePath)

    def readDataLine(self):

        goodLine, newData = self.reader._readDataLine()
        if goodLine:
            self.dataContainer.addDataPoint(newData)

    def getFilePath(self):

        return self.filePath