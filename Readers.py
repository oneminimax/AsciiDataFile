import numpy as np
import re

class Reader(object):

    def __init__(self):

        pass

    def read(self,file_path):

        self._open_file(file_path)
        self._read_header()

        self.field_names, self.units, self.column_number = self.define_field_unit_column()
        self._init_data_interpret()
        
        DC = self._read_data()

        return DC
    
    def __str__(self):

        return str(self.get_field_names())

    def _open_file(self,file_path):
        try:
            self.f_id = open(file_path,'r')

        except IOError:
            print("Cannot open {0:s}".format(file_path))
            raise

    def _read_header(self):

        pass

    def _read_line(self):

        return self.f_id.readline()

    def _line_match(self,line,patern):

        return bool(re.match(patern,line))

    def _new_data_container(self):
        
        return DataContainer(field_names = self.field_names,units = self.units)

    def _init_data_interpret(self):

        field_column_dict = dict()
        for i, field_name in enumerate(self.field_names):
            field_column_dict[field_name] = self.column_number[i]

        self.field_column_dict = field_column_dict

    def _read_data_line(self):

        line = self._read_line()
        splited_line = re.split(self.separator,line)
        if len(splited_line) >= len(self.field_names):
            new_data = self.interpret_data_line(splited_line)
        else:
            new_data = None
        
        return bool(line), new_data

    def _read_data(self):

        DC = self._new_data_container()
    
        while True:
            try:
                keep_reading, new_data = self._read_data_line()
                if keep_reading:
                    if isinstance(new_data,np.ndarray):
                        DC.add_data_point(new_data)
                else:
                    break
            except:
                break

        return DC

    def interpret_data_line(self,splited_line):

        new_data = np.zeros((len(self.field_names),))
        for i_column, channel in enumerate(self.field_names):
            column_number = self.field_column_dict[channel]
            try:
                new_data[i_column] = float(splited_line[column_number])
            except:
                pass

        return new_data



class GenericDataReader(Reader):
    def __init__(self,separator,field_names,units = list(),nb_head_line = 0):
        
        self.separator = separator
        self._field_names = field_names
        self._units = units
        self._nb_head_line = nb_head_line

        Reader.__init__(self)

    def define_field_unit_column(self):

        return self._field_names, self._units, list(range(len(self._field_names)))

    def _read_header(self):
        header_lines = list()

        for n in range(self._nb_head_line):
            header_lines.append(self.f_id.readline())

class MDDataFileReader(Reader):
    separator = ','

    def _read_header(self):

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

        field_names = list()
        units = list()
        for line in header_lines:
            m = re.match("Column .. : (.+)",line)
            if m:
                subLine = m.group(1)
                m1 = re.match(r"([\w -]+)\t(.+)$",subLine)
                m2 = re.match(r"([\w -]+) in (\w+)",subLine)
                if m2:
                    m22 = re.match(r"(.+)\s+(\w+)\s+(\w+)$",m2.group(1).strip())
                    field_names.append(m22.group(2).strip())
                    units.append(m2.group(2).strip())
                elif m1:
                    field_names.append(m1.group(1).strip())
                    units.append(m1.group(2).strip())
                else:
                    field_names.append(subLine.strip())
                    units.append('u.a.')

        self._field_names = field_names
        self._units = units

    def define_field_unit_column(self):

        return self._field_names, self._units, list(range(len(self._field_names)))

class SQUIDDataReader(Reader):

    separator = ','

    def _read_header(self):

        while True:
            line = self._read_line()
            if self._line_match(line,r"\[Data\]"):
                break
        line = self._read_line()

    def define_field_unit_column(self):

        field_names = [
            'time',
            'magnetic field',
            'temperature',
            'long moment',
            'long scan std dev',
            'long algorithm',
            'long reg fit',
            'long percent error'
            ]
        field_units = [
            's',
            'Oe',
            'K',
            'emu',
            'emu',
            None,
            None,
            '%'
            ]
        column_number = [0,2,3,4,5,6,7,8]

        return field_names, field_units, column_number

class PPMSResistivityDataReader(Reader):

    separator = ','

    def __init__(self):
        
        Reader.__init__(self)

    def read(self,file_path,sample_number = 0):
      
        self.sample_number = sample_number

        return Reader.read(self,file_path)
        
    def _read_header(self):

        while True:
            line = self._read_line()
            if self._line_match(line,"\[Data\]"):
                break
        line = self._read_line()

    def define_field_unit_column(self):

        field_names = [
            'time',
            'temperature',
            'magnetic field',
            'sample position'
            ]
        field_units = [
            's',
            'K',
            'Oe',
            'deg',
            ]
        column_number = [1,3,4,5]

        if self.sample_number == 0:
            for i in range(1,4):
                field_names.append('resistance{0:d}'.format(i))
                field_units.append('ohm')
                column_number.append(4 + 2*i)
                field_names.append('current{0:d}'.format(i))
                field_units.append('uA')
                column_number.append(5 + 2*i)

        elif self.sample_number in [1,2,3]:
            field_names.append('resistance')
            field_units.append('ohm')
            column_number.append(4 + 2*self.sample_number)
            field_names.append('current')
            field_units.append('uA')
            column_number.append(5 + 2*self.sample_number)

        return field_names, field_units, column_number

class PPMSACMSDataReader(Reader):

    separator = ','

    def __init__(self,number_of_harmonics = 1):

        self.number_of_harmonics = number_of_harmonics

        Reader.__init__(self)
        

    def _read_header(self):

        while True:
            line = self._read_line()
            if self._line_match(line,"\[Data\]"):
                break
        line = self._read_line()

    def define_field_unit_column(self):

        field_names = [
            'time',
            'temperature',
            'magnetic field',
            'frequency',
            'amplitude',
            'magnetization dc',
            'magnetization std'
            ]
        field_units = [
            's',
            'K',
            'Oe',
            'Hz',
            'Oe',
            'emu',
            'emu'
            ]
        column_number = [1,2,3,4,5,6,7]

        for har in range(self.number_of_harmonics):
            field_names.append("magnetizationReal[{0:d}]".format(har+1))
            field_units.append('')
            column_number.append(8 + 4 * har)
            field_names.append("magnetizationImag[{0:d}]".format(har+1))
            field_units.append('')
            column_number.append(9 + 4 * har)
            field_names.append("magnetizationAbs[{0:d}]".format(har+1))
            field_units.append('')
            column_number.append(10 + 4 * har)
            field_names.append("magnetizationPhase[{0:d}]".format(har+1))
            field_units.append('')
            column_number.append(11 + 4 * har)

        return field_names, field_units, column_number

class DataContainer(object):
    
    def __init__(self,field_names = list(),units = list(),number_of_data_field = 0,tag = ''):

        self.chunkSize = 3

        if len(field_names) > 0:
            self.number_of_data_field = len(field_names)
            self.field_names = field_names
        elif len(units) > 0:
            self.number_of_data_field = len(units)
            self.field_names = self._generic_data_field_names()
        elif number_of_data_field > 0:
            self.number_of_data_field = number_of_data_field
            self.field_names = self._generic_data_field_names()
        else:
            self.number_of_data_field = 0
            self.field_names = []

        if len(units) == self.number_of_data_field:
            self.units = units
        else:
            self.units = self._generic_units()

        self.data_array = np.empty((self.chunkSize,self.number_of_data_field))
        self.number_of_data_point = 0
        self.tag = tag
        

    def __str__(self):

        string = ''
        for field_name in self.field_names:
            string += field_name + "\n"
        string += "number of data point = {0:d}".format(self.number_of_data_point)

        return string

    def __getitem__(self,i):

        self.crop()

        new_dc = self.new_copy()
        new_dc.data_array = self.data_array[i,:]
        new_dc.number_of_data_point = new_dc.data_array.shape[0]

        return new_dc

    def new_copy(self):

        return DataContainer(field_names = self.get_field_names().copy(),units = self.getFieldUnitList().copy())

    def add_data_point(self,new_data):

        if len(new_data) == self.number_of_data_field:
            if self.data_array.shape[0] == self.number_of_data_point:
                self._extend_chunk()
            self.data_array[self.number_of_data_point,:] = new_data
            self.number_of_data_point += 1
        else:
            raise ValueError('New Data Length ({0:d}) is not conform to the number of data fields ({1:d}).'.format(len(new_data),self.number_of_data_field))

    def add_data_field(self,field_name,unit,data):

        if self.number_of_data_field == 0:
            self.field_names.append(field_name)
            self.units.append(unit)
            self.number_of_data_field += 1
            self.data_array = np.zeros((len(data),1))
            self.data_array = np.atleast_2d(data).T
            self.number_of_data_point = self.data_array.shape[0]
        else:
            if len(data) == self.number_of_data_point:
                self.field_names.append(field_name)
                self.units.append(unit)
                self.number_of_data_field += 1
                new_column = np.zeros(self.data_array.shape[0])
                new_column[:self.number_of_data_point] = data
                self.data_array = np.concatenate((self.data_array,np.atleast_2d(new_column).T),axis = 1)

    def _generic_data_field_names(self):

        field_names = list()
        for i in range(self.number_of_data_field):
            field_names.append('Data Field {0:d}'.format(i+1))

        return field_names

    def _generic_units(self):
        units = list()
        for i in range(self.number_of_data_field):
            units.append('a.u.')

        return units

    def _extend_chunk(self):

        new_data_array = np.empty((self.number_of_data_point+self.chunkSize,self.number_of_data_field))
        new_data_array[:self.number_of_data_point,:] = self.data_array
        self.data_array = new_data_array

    def crop(self):

        new_data_array = np.empty((self.number_of_data_point,self.number_of_data_field))
        new_data_array = self.data_array[:self.number_of_data_point,:]
        self.data_array = new_data_array

    def getArray(self):

        return self.data_array[:self.number_of_data_point,:]

    def get_field_names(self):

        return self.field_names

    def get_field_units(self):

        return self.units

    def get_field_index(self,field_name):

        return self.field_names.index(field_name)

    def get_field_by_index(self,index):

        return self.data_array[:self.number_of_data_point,index]

    def get_field_by_name(self,field_name):

        index = self.get_field_index(field_name)
        return self.get_field_by_index(index)

    def get_field_unit(self,field_name):

        index = self.get_field_index(field_name)
        return self.units[index]

    def merge(self,other):

        if set(self.get_field_names()) == set(other.get_field_names()):
            new_dc = self.new_copy()
            new_dc.data_array = np.concatenate((self.data_array[:self.number_of_data_point,:], other.data_array[:other.number_of_data_point,:]),0)
            new_dc.number_of_data_point = new_dc.data_array.shape[0]

            return new_dc

    def extract(self,mask,delete = False):

        self.crop()

        new_dc = self.new_copy()
        new_dc.data_array = self.data_array[mask,:]
        new_dc.number_of_data_point = new_dc.data_array.shape[0]

        if delete:
            
            self.data_array = self.data_array[mask == False,:]
            self.number_of_data_point = self.data_array.shape[0]

        return new_dc



        