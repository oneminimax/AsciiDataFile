import numpy as np

class DataContainer(object):
    
    def __init__(self,column_names = list(),column_units = list(),number_of_columns = 0,tag = '',chunk_size = 10):

        self.chunk_size = chunk_size

        if len(column_names) > 0:
            self.number_of_columns = len(column_names)
            self.column_names = column_names
        elif len(column_units) > 0:
            self.number_of_columns = len(column_units)
            self.column_names = self._generic_data_field_names()
        elif number_of_columns > 0:
            self.number_of_columns = number_of_columns
            self.column_names = self._generic_data_field_names()
        else:
            self.number_of_columns = 0
            self.column_names = []

        if len(column_units) == self.number_of_columns:
            self.column_units = column_units
        else:
            self.column_units = self._generic_units()

        self.data_array = np.empty((self.chunk_size,self.number_of_columns))
        self.number_of_data_points = 0
        self.tag = tag
        

    def __str__(self):

        string = ''
        for column_name in self.column_names:
            string += column_name + "\n"
        string += "number of data points = {0:d}".format(self.number_of_data_points)

        return string

    def __getitem__(self,i):

        self.crop()

        new_data_container = self.empty_copy()
        new_data_container.data_array = self.data_array[i,:]
        new_data_container.number_of_data_points = new_data_container.data_array.shape[0]

        return new_data_container

    def empty_copy(self):
        """ Return a copy of the DataContainer (same column names and units) without the data"""

        return DataContainer(column_names = self.column_names.copy(),column_units = self.column_units.copy())

    def add_data_point(self,new_data):

        if len(new_data) == self.number_of_columns:
            if self.data_array.shape[0] == self.number_of_data_points:
                self._extend_chunk()
            self.data_array[self.number_of_data_points,:] = new_data
            self.number_of_data_points += 1
        else:
            raise ValueError('New Data Length ({0:d}) is not conform to the number of data fields ({1:d}).'.format(len(new_data),self.number_of_columns))

    def add_data_column(self,column_name,column_units,data):

        if self.number_of_columns == 0:
            self.column_names.append(column_name)
            self.column_units.append(column_units)
            self.number_of_columns += 1
            self.data_array = np.zeros((len(data),1))
            self.data_array = np.atleast_2d(data).T
            self.number_of_data_points = self.data_array.shape[0]
        else:
            if len(data) == self.number_of_data_points:
                self.column_names.append(column_name)
                self.column_units.append(column_units)
                self.number_of_columns += 1
                new_column = np.zeros(self.data_array.shape[0])
                new_column[:self.number_of_data_points] = data
                self.data_array = np.concatenate((self.data_array,np.atleast_2d(new_column).T),axis = 1)

    def _generic_data_field_names(self):

        column_names = list()
        for i in range(self.number_of_columns):
            column_names.append('Data Field {0:d}'.format(i+1))

        return column_names

    def _generic_units(self):
        column_units = list()
        for i in range(self.number_of_columns):
            column_units.append('a.u.')

        return column_units

    def _extend_chunk(self):

        new_data_array = np.empty((self.number_of_data_points+self.chunk_size,self.number_of_columns))
        new_data_array[:self.number_of_data_points,:] = self.data_array
        self.data_array = new_data_array

    def crop(self):

        new_data_array = np.empty((self.number_of_data_points,self.number_of_columns))
        new_data_array = self.data_array[:self.number_of_data_points,:]
        self.data_array = new_data_array

    def get_data_array(self):

        return self.data_array[:self.number_of_data_points,:]

    def get_column_names(self):

        return self.column_names

    def get_column_units(self):

        return self.column_units

    def get_column_index(self,column_name):

        return self.column_names.index(column_name)

    def get_column_by_index(self,index):

        return self.data_array[:self.number_of_data_points,index]

    def get_column_by_name(self,column_name):

        index = self.get_column_index(column_name)
        return self.get_column_by_index(index)

    def get_column_unit(self,column_name):

        index = self.get_column_index(column_name)
        return self.column_units[index]

    def merge(self,other):

        if set(self.column_names) == set(other.column_names):
            new_data_container = self.empty_copy()
            new_data_container.data_array = np.concatenate((self.data_array[:self.number_of_data_points,:], other.data_array[:other.number_of_data_points,:]),0)
            new_data_container.number_of_data_points = new_data_container.data_array.shape[0]

            return new_data_container

    def extract(self,mask,delete = False):

        self.crop()

        new_data_container = self.empty_copy()
        new_data_container.data_array = self.data_array[mask,:]
        new_data_container.number_of_data_points = new_data_container.data_array.shape[0]

        if delete:
            self.data_array = self.data_array[mask == False,:]
            self.number_of_data_points = self.data_array.shape[0]

        return new_data_container



        