from os import path

from pint import UnitRegistry, set_application_registry
ureg = UnitRegistry(system = 'mks')

def read_PPMS_Resistivity_data_file():

    from AsciiDataFile.Readers import PPMSResistivityDataReader as Reader

    data_path = 'data/'
    data_file = '20181108_RvsT_3CH_Side1.dat'

    reader = Reader()
    data_curve = reader.read(path.join(data_path,data_file),1,apply_units = True)
    print(data_curve)

    X = data_curve.temperature
    Y = data_curve.resistance

    # print(X)

def read_SQUID_data_file():

    from AsciiDataFile.Readers import SQUIDDataReader as Reader

    data_path = 'data/'
    data_file = '20171003_NiFe_ech1_MvsH_500eO_001.dc.dat'

    reader = Reader()
    data_curve = reader.read(path.join(data_path,data_file),apply_units = True)
    print(data_curve)

    # X = data_container.get_column_by_name('magnetic field')
    # Y = data_container.get_column_by_name('long moment')

def read_PPMS_ACMS_data_file():

    from AsciiDataFile.Readers import PPMSACMSDataReader as Reader

    data_path = 'data/'
    data_file = 'PPMS_ACMS_dataFile.dat'

    reader = Reader()
    data_curve = reader.read(path.join(data_path,data_file),apply_units = True)

    print(data_curve)


def read_PPMS_Heat_Capacity_data_file():

    from AsciiDataFile.Readers import PPMSHeatCapacityDataReader as Reader

    data_path = 'data/'
    data_file = 'Add-135-15Feb2019-1.dat'

    reader = Reader()
    data_curve = reader.read(path.join(data_path,data_file),apply_units = True)
    print(data_curve)

    # X = data_container.get_column_by_name('sample temperature')
    # Y = data_container.get_column_by_name('sample HC')

def read_MD_data_file():

    from AsciiDataFile.Readers import MDDataFileReader as Reader

    data_path = 'data/'
    data_file = '20180711_44.0K.txt'

    reader = Reader()

    data_curve = reader.read(path.join(data_path,data_file),apply_units = True)
    print(data_curve)

    # X = data_container.get_column_by_name('magneticField')
    # Y = data_container.get_column_by_name('VH')

def read_XRD_generic_data_file():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    data_path = 'data/'
    data_file = 'XRD_T2T_dataFile.dat'

    reader = Reader(' ',['angle','signal'],['deg','count'])

    data_curve = reader.read(path.join(data_path,data_file),apply_units = True)
    print(data_curve)

def read_AcquisXD():

    from AsciiDataFile.Readers import GenericDataReader as Reader

    data_path = '/Users/oneminimax/Documents/Projets Physique/PCCO 17 Hall and Lin Res/Transport Data/FAB Samples/20180703B/Acquis'
    data_file = 'VrhoVH-vs-H-42K-HR.txt'

    reader = Reader('\t',['temperature','champ','V1','V2','I'])

    data_container = reader.read(path.join(data_path,data_file))

def write_column_data_file():

    from AsciiDataFile.Writers import DataColumnWriter as Writer
    from AsciiDataFile.Writers import DataColumnWriterWithUnits as WriterWithUnits
    import numpy as np

    data_path = 'data/'
    data_file = 'test_column.txt'
    data_file_wu = 'test_column_wu.txt'

    writer = Writer(path.join(data_path,data_file),auto_numbering = False,separator = '\t')
    writer_wu = WriterWithUnits(path.join(data_path,data_file_wu),auto_numbering = False,separator = '\t',column_width = 20)
    
    X = np.linspace(0,100)*ureg.second
    Y = np.sin(X*1*ureg.hertz)*ureg.meter/ureg.tesla**3*ureg.microsecond

    writer.add_data_column('X',X.magnitude,'{:~}'.format(X.units))
    writer.add_data_column('Y',Y.magnitude,'{:~}'.format(Y.units))


    writer_wu.add_data_column('X',X)
    writer_wu.add_data_column('Y',Y)
    writer_wu.add_data_column('Y',Y)
    writer_wu.add_data_column('Y',Y)

    writer.write()
    writer_wu.write()

def read_column_data_file():

    from AsciiDataFile.Readers import DataColumnReader as Reader

    data_path = 'data/'
    data_file = 'test_column.txt'

    reader = Reader(separator = '\t')
    data_bag = reader.read(path.join(data_path,data_file))
    data_curve = reader.read(path.join(data_path,data_file),apply_units = True)

    print(data_curve)




# read_PPMS_Resistivity_data_file()
# read_PPMS_Heat_Capacity_data_file()
# read_SQUID_data_file()
# read_PPMS_ACMS_data_file()
read_MD_data_file()
# read_XRD_generic_data_file()
# write_column_data_file()
# read_column_data_file()
# read_AcquisXD()
