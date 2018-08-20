class HotReader():
    def __init__(self,reader,dataFile):

        self.reader = reader

        self.dataContainer = reader.read(dataFile)

    def readDataLine(self):

        goodLine, newData = self.reader._readDataLine()
        if goodLine:
            self.dataContainer.addDataPoint(newData)