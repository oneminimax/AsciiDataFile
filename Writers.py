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
            m = re.match('(.+)_(\d{3}).([^.]+)\Z',new_file_name)
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

    def writeData(self,data_array):

        for i in range(data_array.shape[0]):
            self.add_data_point(data_array[i])

    def add_data_point(self,newData):

        lineStr = ''
        for j in range(len(newData)):
            lineStr += "{0:+10.8e}{1:s}".format(newData[j],self.separator)

        if lineStr:
            self.f_id.write(lineStr[:-len(self.separator)] + "\n")
            self.f_id.flush()

class MDDataFileWriter(Writer):
    
    def writeHeader(self,field_names,field_units = list()):

        self.f_id.write("{0:s}\n".format(time.strftime("%c")))
        self.f_id.write("[Header]\n")
        if len(field_units) > 0:
            for i, field_name in enumerate(field_names):
                self.f_id.write("Column {0:2d} : {1:20s}\t{2:s}\n".format(i, field_name, field_units[i]))
        else:
            for i, field_name in enumerate(field_names):
                self.f_id.write("Column {0:2d} : {1:20s}\n".format(i, field_name))

        self.f_id.write("[Header end]\n\n")
        self.f_id.flush()

    def writeDataContainer(self,DC):

        self.writeHeader(DC.field_names,DC.field_units)

        self.writeData(DC.data_array)

