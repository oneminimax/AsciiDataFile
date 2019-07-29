import numpy as np
from os import path
import time
import re

class Writer(object):
    def __init__(self,file_name,auto_numbering = True,separator = ', ',column_width = 15):
        self.file_name = file_name
        self.auto_numbering = auto_numbering
        self.separator = separator
        self.column_width = column_width

        self.column_datas = list()
        self.column_names = list()
        self.column_units = list() #strings
        self.column_number = 0
        self.column_length = 0

        self._open_file()

    def _open_file(self):

        if self.auto_numbering:
            self.check_existing_file()

        self.f_id = open(self.file_name,'w')

    def close(self):

        self.f_id.close()

    def check_existing_file(self):

        new_file_name = self.file_name
        while path.isfile(new_file_name):
            m = re.match(r"(.+)_(\d{3}).([^.]+)\Z",new_file_name)
            if m:
                base_name = m.group(1)
                dig = int(m.group(2))
                ext = m.group(3)
                new_file_name = '{0:s}_{1:03d}.{2:s}'.format(base_name,dig+1,ext)
            else:
                root, ext = path.splitext(new_file_name)
                new_file_name = root + '_002' + ext

        print(self.file_name,'-->',new_file_name)

        self.file_name = new_file_name

    def write_header(self,column_names = None,column_units = None):

        if column_names is None:
            self._write_header(self.column_names,self.column_units)
        else:
            self._write_header(column_names,column_units)

    def _write_header(self,column_names,column_units):
        pass # to be defined by writer type

    def write_datas(self,column_datas = None):

        if column_datas is None:
            self._write_datas(self._make_data_array())
        else:
            self._write_datas(column_datas)

    def _write_datas(self,datas):

        for i in range(datas.shape[0]):
            self.add_data_point(datas[i])

    def write(self,column_names = None,column_units = None,column_datas = None):

        self.write_header(column_names,column_units)
        self.write_datas(column_datas)
        self.f_id.flush()

    def add_data_point(self,data_point):

        line = ''
        for value in data_point:
            if hasattr(value,'units'):
                value = value.magnitude
            
            line += "{value:+{width}.8e}{sep:s}".format(
                value = value,
                width = self.column_width,
                sep = self.separator
                )

        if line:
            self.f_id.write(line[:-len(self.separator)] + "\n")
            self.f_id.flush()

    def _make_data_array(self):

        data_array = np.zeros((self.column_length,self.column_number))
        for i, column_data in enumerate(self.column_datas):
            data_array[:,i] = column_data

        return data_array

    # Build file by column

    def add_data_column(self,name,data,units = None):

        if self.column_number == 0:
            self.column_length = len(data)
        else:
            if not self.column_length == len(data):
                raise('Column length should match previous.')

        self.column_names.append(name)
        self.column_datas.append(data)
        self.column_units.append(units)

        self.column_number += 1

    # build file by piece

    def set_column_names(self,column_names):

        self.column_names = column_names

    def set_column_units(self,column_units):

        self.column_units = column_units

    def set_column_data(self,column_datas):

        self.column_datas = column_datas

class MDDataFileWriter(Writer):
    
    def write_header(self,column_names,column_units = list()):

        self.f_id.write("{0:s}\n".format(time.strftime("%c")))
        self.f_id.write("[Header]\n")
        if len(column_units) > 0:
            for i, column_name in enumerate(column_names):
                self.f_id.write("Column {0:2d} : {1:20s}\t{2:s}\n".format(i, column_name, column_units[i]))
        else:
            for i, column_name in enumerate(column_names):
                self.f_id.write("Column {0:2d} : {1:20s}\n".format(i, column_name))

        self.f_id.write("[Header end]\n\n")
        self.f_id.flush()

class DataColumnWriter(Writer):

    def _write_header(self,column_names,column_units):

        head_line = ''
        for i, column_name in enumerate(column_names):
            if column_units[i] is None:
                column_str = "{0:s}".format(column_name)
            else:
                column_str = "{0:s} ({1:s})".format(column_name,column_units[i])
            head_line += "{col:>{width}s}{sep:s}".format(col = column_str,width = self.column_width,sep = self.separator)

        if head_line:
            self.f_id.write(head_line[:-len(self.separator)] + "\n")
            self.f_id.flush()

class DataColumnWriterWithUnits(DataColumnWriter):

    def add_data_column(self,name,data):

        super().add_data_column(name,data.magnitude,'{:~P}'.format(data.units))

    def write_data_curve(self,data_curve):

        for column_name in data_curve.column_names:
            self.add_data_column(column_name,data_curve.column_dict[column_name])

        self.write_header()
        self.write_datas()
