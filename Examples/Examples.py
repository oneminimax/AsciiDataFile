from os import path

def read_PPMS_ACMS_dataFile():

    from AsciiDataFile.Readers import PPMSACMSDataReader as Reader

    dataPath = 'data/'
    dataFile = 'PPMS_ACMS_dataFile.dat'

    reader = Reader(path.join(dataPath,dataFile))
    print(reader)

    X = reader.getFieldByName('magnetic field')
    Y = reader.getFieldByName('magnetization dc')


read_PPMS_ACMS_dataFile()
