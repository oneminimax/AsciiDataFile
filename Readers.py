import numpy as np
import re
from .DataContainer import DataCurve, DataCurvePint

class Reader(object):

    codec = 'utf-8'

    def __init__(self):

        pass

    def __str__(self):

        return str(self.get_column_names())

    def read(self,file_path,use_units = True):
        """ Read a file 

        file_path : full path to the data file

        Return the data formated into a DataContainer
        """

        self._open_file(file_path)
        self._read_header()

        self.column_names, self.column_units, self.column_numbers = self.define_column_names_units_numbers()
        self._init_data_mapper()
        
        data_curve = self._read_data(use_units)

        return data_curve
            

    def _open_file(self,file_path):
        """ Open a file. Set the file as the active file. 
        
        file_path : full path to the data file

        Store the file ID in the Reader
        """

        try:
            self.f_id = open(file_path,'r',encoding = self.codec)

        except IOError:
            print("Cannot open {0:s}".format(file_path))
            raise

    def _new_data_curve(self,use_units = True):
        """ Create the DataContainer with the field names and units """
        
        if use_units:
            data_curve = DataCurvePint(column_names = self.column_names,column_units_labels = self.column_units)
        else:
            data_curve = DataCurve(column_names = self.column_names,column_units_labels = self.column_units)

        return data_curve

    def define_column_names_units_numbers(self):
        """ Define three list : column_names, column_units and column_numbers. 
        This is Reader dependant. 
        Can be user defined for GenericDataReader
        """

        pass

    def _init_data_mapper(self):
        """ Initialise the data_mapper 

        The data_mapper is a dict where keys are data field name and values are data column number
        """

        data_mapper = dict()
        for i, column_name in enumerate(self.column_names):
            data_mapper[column_name] = self.column_numbers[i]

        self.data_mapper = data_mapper

    def _read_data_line(self):
        """ Read a data line

        Return a bool (True if line succesfully read) 
        and an array with the data in the same order as column_names
        """

        line = self.f_id.readline()
        splited_line = re.split(self.separator,line)
        if len(splited_line) >= len(self.column_names):
            new_data = self.map_data_line(splited_line)
        else:
            new_data = None
        
        return bool(line), new_data

    def _read_header(self):
        """ Read the header of the active data file. This is Reader dependant.
        Should fill self._column_names and self._units with relevant strings
        """

        pass

    def _read_data(self,use_units):
        """ Read the data part of the file 

        Return the data formated into a DataContainer
        """

        data_curve = self._new_data_curve(use_units)
        while True:
            # try:
                keep_reading, new_data = self._read_data_line()
                if keep_reading:
                    if isinstance(new_data,np.ndarray):
                        data_curve.add_data_point(new_data)
                else:
                    break
            # except:
                # break

        data_curve.crop()

        return data_curve

    def map_data_line(self,splited_line):
        """ Map a splited data line and map selected column in the same order as column_names """

        new_data = np.zeros((len(self.column_names),))
        for i_column, channel in enumerate(self.column_names):
            column_numbers = self.data_mapper[channel]
            try:
                new_data[i_column] = float(splited_line[column_numbers])
            except:
                pass

        return new_data

    def get_column_names(self):

        return self.column_names

    def get_column_units(self):

        return self.column_units

    def get_column_index(self,column_name):

        return self.column_names.index(column_name)

class GenericDataReader(Reader):
    """ GenericDataReader can be customized to read any ASCII character separated data file """
    def __init__(self,separator,column_names,column_units = list(),nb_head_lines = 0):
        """ Initialize a GenericDataReader

        separator : Character(s) separating the data (ex : ',' or '\t')
        column_names : List of data columns
        column_units : List of units string in the same order as column_names (optional)
        nb_head_lines : Number of lines to skip at the begining of the file (default = 0)
        """
        
        self.separator = separator
        self._column_names = column_names
        self._units = column_units
        self._nb_head_lines = nb_head_lines

        super().__init__()

    def define_column_names_units_numbers(self):

        return self._column_names, self._units, list(range(len(self._column_names)))

    def _read_header(self):
        """ Read the header of the active data file."""

        header_lines = list()

        for n in range(self._nb_head_lines):
            header_lines.append(self.f_id.readline())

class DataColumnReader(Reader): # todo
    def __init__(self,separator = ','):

        super().__init__()

        self.separator = separator

    def _read_header(self):
        header_line = self.f_id.readline()
        column_heads = re.split(self.separator,header_line)

        column_names = list()
        column_units = list()

        for column_head in column_heads:
            column_head = column_head.strip()
            m_wu = re.match(r"(.+)\((.+)\)",column_head)
            if m_wu:
                column_name = m_wu.group(1).strip()
                column_unit = m_wu.group(2).strip()
            else:
                column_name = column_head
                column_unit = None

            column_names.append(column_name)
            column_units.append(column_unit)

        self._column_names = column_names
        self._units = column_units

    def define_column_names_units_numbers(self):

        return self._column_names, self._units, list(range(len(self._column_names)))

class MDDataFileReader(Reader):
    """ MDDataFileReader read in house data file where the header contains the information
    about the column names and units."""
    
    def __init__(self):

        super().__init__()
        self.separator = ','

    def _read_header(self):
        """ Read the header lines. Store the column names and units. """

        header_lines = list()

        while True:
            line = self.f_id.readline()
            if not line:
                break
            m1 = re.match(r"\[Header\]",line)
            m2 = re.match(r"\[Instrument List\]",line)
            if m1 or m2:
                break

        while True:
            line = self.f_id.readline()
            if not line:
                break
            m1 = re.match(r"\[Header end\]",line)
            m2 = re.match(r"\[Instrument List end\]",line)
            if m1 or m2:
                break
            else:
                header_lines.append(line.strip())

        column_names = list()
        column_units = list()
        for line in header_lines:
            m = re.match("Column .. : (.+)",line)
            if m:
                subLine = m.group(1)
                m1 = re.match(r"([\w -]+)\t(.+)$",subLine)
                m2 = re.match(r"([\w -]+) in (\w+)",subLine)
                if m2:
                    m22 = re.match(r"(.+)\s+(\w+)\s+(\w+)$",m2.group(1).strip())
                    column_names.append(m22.group(2).strip())
                    column_units.append(m2.group(2).strip())
                elif m1:
                    column_names.append(m1.group(1).strip())
                    column_units.append(m1.group(2).strip())
                else:
                    column_names.append(subLine.strip())
                    column_units.append('u.a.')

        self._column_names = column_names
        self._units = column_units

    def define_column_names_units_numbers(self):

        return self._column_names, self._units, list(range(len(self._column_names)))

class QDReader(Reader):

    def _read_header(self):
        """ Not implemented yet. Just skip to the data part. """

        while True:
            line = self.f_id.readline()
            if bool(re.match(r"\[Data\]",line)):
                break
        line = self.f_id.readline()

    def define_column_names_units_numbers(self):

        column_names = list()
        column_units = list()
        column_numbers = list()
        for column_tuple in self.column_tuples:
            column_names.append(column_tuple[1])
            column_units.append(column_tuple[2])
            column_numbers.append(column_tuple[0])

        return column_names, column_units, column_numbers

class SQUIDDataReader(QDReader):
    """ SQUIDDataReader read Quantum Design SQUID data file format."""

    def __init__(self):
        
        super().__init__()

        self.separator = ','
        self.column_tuples = [
            (0,'time','s'),
            (2,'magnetic field','Oe'),
            (3,'temperature','K'),
            (4,'long moment','mA/m**2'), #ureg.milliampere*ureg.meter**2
            (5,'long scan std dev','mA/m**2'),
            (6,'long algorithm',None),
            (7,'long reg fit',None),
            (8,'long percent error','%')
            ]

class PPMSResistivityDataReader(QDReader):
    """ SQUIDDataReader read Quantum Design PPMS resistivity data file format."""

    def __init__(self):
        
        super().__init__()

        self.separator = ','
        self.column_tuples = [
            (1,'time','s'),
            (3,'temperature','K'),
            (4,'magnetic field','Oe'),
            (5,'sample position','deg')
            ]

    def read(self,file_path,sample_number = 0,*vargs,**kwargs):

        self.add_channel_column_tuples(sample_number)

        return Reader.read(self,file_path,*vargs,**kwargs)

    def add_channel_column_tuples(self,sample_number):
        if sample_number == 0:
            for i in range(1,4):
                self.column_tuples.append((4 + 2*i,'resistance{0:d}'.format(i),'ohm'))
                self.column_tuples.append((5 + 2*i,'current{0:d}'.format(i),'uA'))

        elif sample_number in [1,2,3]:
            self.column_tuples.append((4 + 2*sample_number,'resistance','ohm'))
            self.column_tuples.append((5 + 2*sample_number,'current','uA'))

class PPMSACMSDataReader(QDReader):
    """ SQUIDDataReader read Quantum Design PPMS ACMS data file format."""

    def __init__(self,number_of_harmonics = 1):

        super().__init__()

        self.number_of_harmonics = number_of_harmonics
        self.separator = ','
        self.column_tuples = [
            (1,'time','s'),
            (2,'temperature','K'),
            (3,'magnetic field','Oe'),
            (4,'frequency','Hz'),
            (5,'amplitude','Oe'),
            (6,'magnetization dc','mA/m**2'),
            (7,'magnetization std','mA/m**2')
            ]

        

    def add_harmonics_column_tuples(self,number_of_harmonics):
        for har in range(self.number_of_harmonics):
            self.column_tuples.append((8 + 4 * har,'magnetizationReal[{0:d}]'.format(har+1),''))
            self.column_tuples.append((9 + 4 * har,'magnetizationImag[{0:d}]'.format(har+1),''))
            self.column_tuples.append((10 + 4 * har,'magnetizationAbs[{0:d}]'.format(har+1),''))
            self.column_tuples.append((11 + 4 * har,'magnetizationPhase[{0:d}]'.format(har+1),''))

class PPMSHeatCapacityDataReader(QDReader):
    """ SQUIDDataReader read Quantum Design PPMS ACMS data file format."""

    codec = 'cp1252'

    def __init__(self):

        super().__init__()
        
        self.separator = ','
        self.column_tuples = [
            (0,'time','s'),
            (1,'PPMS status',None),
            (2,'puck temperature','K'),
            (3,'system temperature','K'),
            (4,'magnetic field','Oe'),
            (5,'pressure','torr'),
            (6,'sample temperature','K'),
            (7,'temperature rise','K'),
            (8,'sample HC','uJ/K'),
            (9,'sample HC err','uJ/K'),
            (10,'addenda HC','uJ/K'),
            (11,'addenda HC err','uJ/K'),
            (12,'total HC','uJ/K'),
            (13,'total HC err','uJ/K'),
            (14,'fit deviation',None),
            (15,'tau1','s'),
            (16,'tau2','s'),
            (17,'sample coupling','%'),
            (18,'debye temperature','K'),
            (19,'debye temperature err','K'),
            (20,'cal correction',None)
            ]


