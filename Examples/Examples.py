from os import path

def read_PPMS_ACMS_dataFile():

    from AsciiDataFile.Readers import PPMSACMSDataReader as Reader

    dataPath = 'data/'
    dataFile = 'PPMS_ACMS_dataFile.dat'

    reader = Reader()
    DC = reader.read(path.join(dataPath,dataFile))
    print(DC)

    X = DC.getFieldByName('magnetic field')
    Y = DC.getFieldByName('magnetization dc')

    # print(Y)

def read_XRD_generic_dataFile():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    dataPath = 'data/'
    dataFile = 'XRD_T2T_dataFile.dat'

    reader = Reader(' ',['angle','signal'])

    DC = reader.read(path.join(dataPath,dataFile))
    print(DC)

    X = DC.getFieldByName('angle')
    Y = DC.getFieldByName('signal')


read_PPMS_ACMS_dataFile()
read_XRD_generic_dataFile()
