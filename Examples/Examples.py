from os import path

def read_PPMS_ACMS_dataFile():

    from AsciiDataFile.Readers import PPMSACMSDataReader as Reader

    dataPath = 'data/'
    dataFile = 'PPMS_ACMS_dataFile.dat'

    reader = Reader()
    dataContainer = reader.read(path.join(dataPath,dataFile))
    print(dataContainer)

    X = dataContainer.getFieldByName('magnetic field')
    Y = dataContainer.getFieldByName('magnetization dc')

def read_MD_dataFile():

    from AsciiDataFile.Readers import MDDataFileReader as Reader

    dataPath = 'data/'
    dataFile = '20180711_44.0K.txt'

    reader = Reader()

    dataContainer = reader.read(path.join(dataPath,dataFile))
    print(dataContainer)

    X = dataContainer.getFieldByName('magneticField')
    Y = dataContainer.getFieldByName('VH')

def read_XRD_generic_dataFile():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    dataPath = 'data/'
    dataFile = 'XRD_T2T_dataFile.dat'

    reader = Reader(' ',['angle','signal'])

    dataContainer = reader.read(path.join(dataPath,dataFile))
    print(dataContainer)

    X = dataContainer.getFieldByName('angle')
    Y = dataContainer.getFieldByName('signal')

def readAcquisXD():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    dataPath = '/Users/oneminimax/Documents/Projets Physique/PCCO 17 Hall and Lin Res/Transport Data/FAB Samples/20180703B/Acquis'
    dataFile = 'VrhoVH-vs-H-42K-HR.txt'

    reader = Reader('\t',['temperature','champ','V1','V2','I'])

    dataContainer = reader.read(path.join(dataPath,dataFile))


# read_PPMS_ACMS_dataFile()
read_MD_dataFile()
# read_XRD_generic_dataFile()
# readAcquisXD()
