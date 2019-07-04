import numpy as np
from os import path
import time
import re

class Writer(object):
    def __init__(self,file_name,auto_numbering = True,separator = ','):
        self.file_name = file_name
        self.auto_numbering = auto_numbering
        self.separator = separator

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

    def write_data(self,data_array):

        for i in range(data_array.shape[0]):
            self.add_data_point(data_array[i])

    def add_data_point(self,data_point):

        line = ''
        for value in data_point:
            line += "{0:+10.8e}{1:s}".format(value,self.separator)

        if line:
            self.f_id.write(line[:-len(self.separator)] + "\n")
            self.f_id.flush()

class MDDataFileWriter(Writer):
    
    def write_header(self,field_names,field_units = list()):

        self.f_id.write(r"{0:s}\n".format(time.strftime("%c")))
        self.f_id.write(r"[Header]\n")
        if len(field_units) > 0:
            for i, field_name in enumerate(field_names):
                self.f_id.write(r"Column {0:2d} : {1:20s}\t{2:s}\n".format(i, field_name, field_units[i]))
        else:
            for i, field_name in enumerate(field_names):
                self.f_id.write(r"Column {0:2d} : {1:20s}\n".format(i, field_name))

        self.f_id.write("[Header end]\n\n")
        self.f_id.flush()

    def write_data_container(self,data_container):

        self.write_header(data_container.field_names,data_container.field_units)

        self.write_data(data_container.data_array)

class DataColumnWriter(Writer):

    def __init__(self,*args,**kwargs):

        Writer.__init__(self,*args,**kwargs)

        self.column_datas = list()
        self.column_names = list()
        self.column_number = 0
        self.column_length = 0

    def add_data_column(self,name,data):

        if self.column_number == 0:
            self._add_data_column(name,data)
            self.column_length = len(data)
        else:
            if self.column_length == len(data):
                self._add_data_column(name,data)
            else:
                raise('Column length should match previous.')

    def _add_data_column(self,name,data):

        self.column_names.append(name)
        self.column_datas.append(data)
        self.column_number += 1

    def _make_data_array(self):

        data_array = np.zeros((self.column_length,self.column_number))
        for i, column_data in enumerate(self.column_datas):
            data_array[:,i] = column_data

        return data_array

    def _write_head_line(self):

        head_line = ''
        for column_name in self.column_names:
            head_line += "{0:15s}{1:s}".format(column_name,self.separator)

        if head_line:
            self.f_id.write(head_line[:-len(self.separator)] + "\n")

    def write(self):

        self._write_head_line()  
        self.write_data(self._make_data_array())
        self.f_id.flush()
