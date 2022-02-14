import numpy as np
from os import path
import time
import re

class Writer(object):
    def __init__(self,file_name,auto_numbering = True,separator = ', ',column_width = 15,decimal = '.'):
        self.file_name = file_name
        self.auto_numbering = auto_numbering
        self.separator = separator
        self.column_width = column_width
        self.decimal = decimal

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

    def write_header(self,column_names,column_units = None):

        self.column_number = len(column_names)
        self._write_header(column_names,column_units)

    def _write_header(self,column_names,column_units = None):
        pass # to be defined by writer type

    def write_values(self,values):

        if self.column_number == 0:
            self._write_datas(values)
        else:
            values_shape = values.shape
            if values_shape[0] == self.column_number:
                self._write_values(values)
            elif values_shape[1] == self.column_number:
                self._write_values(np.transpose(values))
            else:
                raise()

    def _write_values(self,values):

        for i in range(values.shape[0]):
            self.add_data_point(values[i,:])

    def write(self,column_names,values,column_units = None):

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

        if self.decimal is ',':
            line = line.replace('.',',')


        if line:
            self.f_id.write(line[:-len(self.separator)] + "\n")
            self.f_id.flush()

    def write_data_curve(self,data_curve):

        column_names = data_curve.get_column_names()
        column_units = data_curve.get_column_unitss()

        self._write_header(column_names,column_units)
        self._write_values(data_curve.get_values_array())

class MDDataFileWriter(Writer):
    
    def write_header(self,column_names,column_units = None):

        self.f_id.write("{0:s}\n".format(time.strftime("%c")))
        self.f_id.write("[Header]\n")
        if column_units is None:
            for i, column_name in enumerate(column_names):
                self.f_id.write("Column {0:2d} : {1:20s}\n".format(i, column_name))
        else:
            for i, column_name in enumerate(column_names):
                self.f_id.write("Column {0:2d} : {1:20s}\t{2:s}\n".format(i, column_name, column_units[i]))

        self.f_id.write("[Header end]\n\n")
        self.f_id.flush()

class DataColumnWriter(Writer):

    def _write_header(self,column_names,column_units = None):

        head_line = ''
        for i, column_name in enumerate(column_names):
            if column_units[i] is None:
                column_str = "{0:s}".format(column_name)
            else:
                column_str = "{0:s}({1:s})".format(column_name,column_units[i])
            head_line += "{col:>{width}s}{sep:s}".format(col = column_str,width = self.column_width,sep = self.separator)

        if head_line:
            self.f_id.write(head_line[:-len(self.separator)] + "\n")
            self.f_id.flush()
    
