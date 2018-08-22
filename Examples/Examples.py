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

def readAcquisXD():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    dataPath = '/Users/oneminimax/Documents/Projets Physique/PCCO 17 Hall and Lin Res/Transport Data/FAB Samples/20180703B/Acquis'
    dataFile = 'VrhoVH-vs-H-42K-HR.txt'

    reader = Reader('\t',['temperature','champ','V1','V2','I'])

    DC = reader.read(path.join(dataPath,dataFile))


# read_PPMS_ACMS_dataFile()
# read_XRD_generic_dataFile()
readAcquisXD()
