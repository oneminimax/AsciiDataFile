from os import path

def read_PPMS_ACMS_dataFile():

    from AsciiDataFile.Readers import PPMSACMSDataReader as Reader

    data_path = 'data/'
    data_file = 'PPMS_ACMS_dataFile.dat'

    reader = Reader()
    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_field_by_name('magnetic field')
    Y = data_container.get_field_by_name('magnetization dc')

def read_MD_dataFile():

    from AsciiDataFile.Readers import MDDataFileReader as Reader

    data_path = 'data/'
    data_file = '20180711_44.0K.txt'

    reader = Reader()

    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_field_by_name('magneticField')
    Y = data_container.get_field_by_name('VH')

def read_XRD_generic_dataFile():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    data_path = 'data/'
    data_file = 'XRD_T2T_dataFile.dat'

    reader = Reader(' ',['angle','signal'])

    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_field_by_name('angle')
    Y = data_container.get_field_by_name('signal')

def readAcquisXD():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    data_path = '/Users/oneminimax/Documents/Projets Physique/PCCO 17 Hall and Lin Res/Transport Data/FAB Samples/20180703B/Acquis'
    data_file = 'VrhoVH-vs-H-42K-HR.txt'

    reader = Reader('\t',['temperature','champ','V1','V2','I'])

    data_container = reader.read(path.join(data_path,data_file))


read_PPMS_ACMS_dataFile()
# read_MD_dataFile()
# read_XRD_generic_dataFile()
# readAcquisXD()
