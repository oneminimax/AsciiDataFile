from os import path

def read_PPMS_Resistivity_data_file():

    from AsciiDataFile.Readers import PPMSResistivityDataReader as Reader

    data_path = 'data/'
    data_file = '20181108_RvsT_3CH_Side1.dat'

    reader = Reader()
    data_container = reader.read(path.join(data_path,data_file),1)
    print(data_container)

    X = data_container.get_column_by_name('temperature')
    Y = data_container.get_column_by_name('resistance')

def read_PPMS_SQUID_data_file():

    from AsciiDataFile.Readers import SQUIDDataReader as Reader

    data_path = 'data/'
    data_file = '20171003_NiFe_ech1_MvsH_500eO_001.dc.dat'

    reader = Reader()
    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_column_by_name('magnetic field')
    Y = data_container.get_column_by_name('long moment')

def read_PPMS_ACMS_data_file():

    from AsciiDataFile.Readers import PPMSACMSDataReader as Reader

    data_path = 'data/'
    data_file = 'PPMS_ACMS_dataFile.dat'

    reader = Reader()
    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_column_by_name('magnetic field')
    Y = data_container.get_column_by_name('magnetization dc')

    sub_data_container = data_container.extract(X < 2e3)

    print(sub_data_container)

def read_PPMS_Heat_Capacity_data_file():

    from AsciiDataFile.Readers import PPMSHeatCapacityDataReader as Reader

    data_path = 'data/'
    data_file = 'Add-135-15Feb2019-1.dat'

    reader = Reader()
    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_column_by_name('sample temperature')
    Y = data_container.get_column_by_name('sample HC')

def read_MD_data_file():

    from AsciiDataFile.Readers import MDDataFileReader as Reader

    data_path = 'data/'
    data_file = '20180711_44.0K.txt'

    reader = Reader()

    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_column_by_name('magneticField')
    Y = data_container.get_column_by_name('VH')

def read_XRD_generic_data_file():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    data_path = 'data/'
    data_file = 'XRD_T2T_dataFile.dat'

    reader = Reader(' ',['angle','signal'])

    data_container = reader.read(path.join(data_path,data_file))
    print(data_container)

    X = data_container.get_column_by_name('angle')
    Y = data_container.get_column_by_name('signal')

def read_AcquisXD():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    data_path = '/Users/oneminimax/Documents/Projets Physique/PCCO 17 Hall and Lin Res/Transport Data/FAB Samples/20180703B/Acquis'
    data_file = 'VrhoVH-vs-H-42K-HR.txt'

    reader = Reader('\t',['temperature','champ','V1','V2','I'])

    data_container = reader.read(path.join(data_path,data_file))

def write_column_data_file():

    from AsciiDataFile.Writers import DataColumnWriter as Writer
    import numpy as np

    data_path = 'data/'
    data_file = 'test_column.txt'

    writer = Writer(path.join(data_path,data_file),auto_numbering = False,separator = '\t')
    
    X = np.linspace(0,100)
    Y = np.sin(X)

    writer.add_data_column('X',X)
    writer.add_data_column('Y',Y)

    writer.write()

# read_PPMS_Resistivity_data_file()
# read_PPMS_Heat_Capacity_data_file()
# read_PPMS_SQUID_data_file()
# read_PPMS_ACMS_data_file()
# read_MD_data_file()
# read_XRD_generic_data_file()
write_column_data_file()
# read_AcquisXD()
