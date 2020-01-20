import numpy as np

from scipy.interpolate import interp1d

class Column(object):

    def __init__(self,name,units,data = list()):

        self.name = name
        self.set_units(units)
        self.set_data(data)

        self.update_length()

    def __len__(self):

        return len(self.data)

    def __str__(self):

        return f'{self.name} ({self.units}) : {self.data_length} points'

    def __repr__(self):

        return f'{self.name} ({self.units}) : {self.data_length} points'

    def set_units(self,units):

        self.units = units

    def set_data(self,data):

        self.data = np.array(data)

    def get_data(self):

        return self.data[:self.data_length]

    def get_units(self):

        return self.units

    def rename(self,name):

        self.name = name

    def add_data_point(self,value):

        self.data[self.data_length] = value
        
        self.data_length += 1

    def filter(self,mask):

        self.set_data(self.data[mask])
        self.update_length()

    def update_length(self):

        self.data_length = len(self.data)
        self.extend_data_length = len(self.data)

    def _extend_chunk(self,chunk_size):

        larger_data = np.zeros((self.data_length + chunk_size,))
        larger_data[:self.data_length] = self.data
        self.data = larger_data
        self.extend_data_length = self.data_length + chunk_size

    def _crop(self):

        self.data = self.data[:self.data_length]
        self.extend_data_length = self.data_length+0

    def _copy(self):

        return self.__class__(self.name,self.units,self.get_data())

    def equals_within_tolerance(self,value,tolerance):

        return np.abs((self.get_data() - value)) < tolerance

    def in_range(self,limits):

        data = self.get_data()
        return np.logical_and(data > limits[0], data < limits[1])

class DataCurve(object):

    def __init__(self,*vargs,**kwargs):

        self.chunk_size = 100

        self.parameter_dict = dict()
        self.column_dict = dict()

        self.data_length = 0
        self.extend_data_length = 0
        self.name = 'DataCurve'

        for arg in vargs:
            if isinstance(arg,DataCurve):
                self.set_column_dict(arg.column_dict)
                self.set_parameter_dict(arg.parameter_dict)
                self.data_length = arg.data_length
                self.extend_data_length = self.extend_data_length

        if 'column_names' in kwargs and 'column_units_labels' in kwargs:
            self.init_columns(kwargs['column_names'],kwargs['column_units_labels'])
        elif 'column_dict' in kwargs:
            self.set_column_dict(kwargs['column_dict'])

    def __getattr__(self,name):

        if name in self.column_dict:
            return self.column_dict[name].get_data()
        
        var_name = name.replace('_',' ')
        if var_name in self.column_dict:
            return self.column_dict[var_name].get_data()

    def __str__(self):

        info_str = f'{self.name:s} ({self.data_length:d} data points)\n'
        if self.parameter_dict:
            for parameter_name in self.parameter_dict:
                info_str += parameter_name + ' : ' + str(self.parameter_dict[parameter_name]) + ', '
        if self.column_dict:
            for column_name, column in self.column_dict.items():
                info_str += ' ' + column_name + ' (' + str(column.units) + ')\n'

        return info_str[:-1]

    def _copy_column_dict(self):

        new_column_dict = dict()
        for column_name, column in self.column_dict.items():
            new_column_dict[column_name] = column._copy()

        return new_column_dict

    def convert(self,new_class):

        return new_class(self)

    def init_columns(self,column_names,column_units_labels = []):
        
        if len(column_names) == len(column_units_labels):
            for i, (column_name,column_units_label) in enumerate(zip(column_names,column_units_labels)):
                self.add_column(column_name,column_units_label)
        else:
            for i, column_name in enumerate(column_names):
                self.add_column(column_name,'')

    def add_column(self,column_name,column_units_label,column_data = None):

        if column_data is None:
            column_data = np.empty([0,])

        if self.data_length:
            if not len(column_data) == self.data_length:
                raise Exception('Data length must be the same')
        else:
            self.data_length = len(column_data)

        self.column_dict[column_name] = Column(column_name,column_units_label,column_data)

    def add_parameter(self,parameter_name,parameter_value):

        self.parameter_dict[parameter_name] = parameter_value

    def update_column(self,column_name,column_data,units = None):

        if not len(column_data) == self.data_length:
            raise Exception('Data length must be the same')

        self.column_dict[column_name].set_data(column_data)
        if units is not None:
            self.column_dict[column_name].set_units(units)

    def rename_column(self,old_name,new_name):

        if old_name in self.get_column_names():
            self.column_dict[old_name].rename(new_name)
            self.column_dict[new_name] = self.column_dict.pop(old_name)

    def add_data_point(self,values):

        if not len(values) == self.column_number():
            raise ValueError('New Data dimension ({0:d}) is not conform to the number of data columns ({1:d}).'.format(len(values),self.column_number()))

        if self.extend_data_length == self.data_length:
            self._extend_chunk()

        if isinstance(values,dict):
            new_data = values
            if not new_data.keys() == self.column_dict.keys():
                ValueError('Column name should already be present in DataCurve')

        elif isinstance(values,list) or isinstance(values,np.ndarray):
            new_data = dict(zip(self.get_column_names(),values))

        for column_name in self.column_dict:
            self.column_dict[column_name].add_data_point(new_data[column_name])
        
        self.data_length += 1

    def column_number(self):

        return len(self.column_dict)

    def _extend_chunk(self):

        for column_name in self.column_dict:
            self.column_dict[column_name]._extend_chunk(self.chunk_size)
        self.extend_data_length = self.data_length+self.chunk_size

    def _crop(self):

        for column_name in self.column_dict:
            self.column_dict[column_name]._crop()

        self.extend_data_length = self.data_length+0


    def _check_column_name(self):

        for column_name, column in self.column_dict.items():
            column.rename(column_name)

    ''' Sets '''

    def set_column_dict(self,column_dict):

        data_lengths = list()
        for column_name in column_dict:
            data_lengths.append(len(column_dict[column_name]))

        data_length = np.unique(data_lengths)
        if len(data_length) == 1:
            self.column_dict = column_dict
            self.data_length = data_length[0]
            self.extend_data_length = data_length[0]
        else:
            raise Exception('Data length must be the same')

        self._check_column_name()

    def set_parameter_dict(self,parameter_dict):

        self.parameter_dict = parameter_dict

    ''' Gets '''

    def get_column_names(self):

        return list(self.column_dict.keys())

    def get_column_unitss(self):

        column_unitss = list()

        for column_name, column in self.column_dict.items():
            column_unitss.append(self.column_dict[column_name].get_units())

        return column_unitss

    def get_column_data(self,column_name):

        return self.column_dict[column_name].get_data()

    def get_column(self,column_name):

        return self.column_dict[column_name].get_data()

    def get_columns(self,column_names):

        columns = list()
        for column_name in column_names:
            columns.append(self.get_column_data(column_name))

        return columns

    def get_column_units(self,column_name):

        return self.column_dict[column_name].get_units()

    # Manipulation methods

    def filter(self,mask,new_curve = False):

        if new_curve:
            column_dict = self._copy_column_dict()
        else:
            column_dict = self.column_dict

        for column_name, column in column_dict.items():
            column.filter(mask)

        if new_curve:
            return self.__class__(column_dict = column_dict,parameter_dict = self.parameter_dict)

    def filter_column(self,column_names):

        new_column_dict = dict()
        for column_name in column_names:
            column = self.column_dict[column_name]
            new_column_dict[column_name] = Column(column_name,column.units,column.data)
            #getattr(self,column_name)

        self.set_column_dict(new_column_dict)

        return self

    def sort_by(self,column_name):

        sort_i = np.argsort(self.column_dict[column_name].get_data())
        new_column_dict = dict()
        for column_name, column in self.column_dict.items():
            column.set_data(column.get_data()[sort_i])

    def select_value(self,column_name,value,tolerance,new_curve = False):
        
        mask = self.column_dict[column_name].equals_within_tolerance(value,tolerance)
        return self.filter(mask,new_curve)

    def select_range(self,column_name,limits,new_curve = False):

        mask = self.column_dict[column_name].in_range(limits)
        return self.filter(mask,new_curve)

    def select_direction(self,column_name,direction,new_curve = False):

        mask = np.gradient(self.get_column_data(column_name))*direction > 0
        return self.filter(mask,new_curve)

    def average_multiple_measurement(self,select_column_name,value_step):

        unique_values = np.unique(np.round(self.get_column_data(select_column_name)/value_step))*value_step
        
        select_column_data = self.get_column_data(select_column_name)
        for column_name, column in self.column_dict.items():
            new_data = np.zeros(unique_values.shape)
            for i_value, value in enumerate(unique_values):
                ind = (select_column_data - value)**2 < value_step**2/2
                new_data[i_value] = np.average(column.get_data()[ind])

            column.set_data(new_data)
        self.data_length = len(unique_values)
        self.extend_data_length = len(unique_values)

    def interpolate(self,x_column_name,x_values):

        x_column_data = self.get_column_data(x_column_name)
        new_column_dict = dict()
        for column_name, column in self.column_dict.items():
            if column_name == x_column_name:
                new_column = Column(column_name,column.units,x_values)
            else:
                new_column = Column(column_name,column.units,self.y_at_x(x_column_name,column_name,x_values))

            new_column_dict[column_name] = new_column

        return self.__class__(column_dict = new_column_dict,parameter_dict = self.parameter_dict)

    def y_at_x(self,x_column_name,y_column_name,x_values):

        f = interp1d(self.get_column_data(x_column_name),self.get_column_data(y_column_name),fill_value='extrapolate')

        return f(x_values)

    def symetrize(self,x_column_name,sym_y_column_names = list(),antisym_y_column_names = list(),x_values = None,x_step = None):

        if x_values is None and not x_step is None:
            x_values = self.auto_sym_x_values(x_column_name,x_step)
        elif not x_values is None and x_step is None:
            pass
        else:
            raise(ValueError('Most provide x_values or x_step'))

        sym_column_dict = dict()
        for column_name, column in self.column_dict.items():
            f = interp1d(self.get_column_data(x_column_name),column.data,fill_value='extrapolate')
            if column_name in sym_y_column_names:
                sym_data = (f(x_values) + f(-x_values))/2
            elif column_name in antisym_y_column_names:
                sym_data = (f(x_values) - f(-x_values))/2
            else:
                continue

            sym_column_dict[column_name] = Column(column_name,column.units,sym_data)
        
        return self.set_column_dict(sym_column_dict)

    def auto_sym_x_values(self,x_column_name,x_step):

        max_x_value = np.max(np.round(self.get_column_data(x_column_name)/x_step))*x_step

        return np.linspace(0,max_x_value,int(max_x_value/x_step)+1)

    def get_values_array(self):

        self._crop()
        values_array = np.zeros((self.data_length,self.column_number()))
        for i, column_name in enumerate(self.column_dict):
            values_array[:,i] = self.column_dict[column_name].get_data()

        return values_array

    def append(self,other):

        new_column_dict = dict()
        for column_name, column in self.column_dict.items():
            X1 = self.column_dict[column_name].get_data()
            X2 = other.column_dict[column_name].get_data()
            new_data = np.concatenate((X1,X2))

            new_column_dict[column_name] = Column(column_name,column.units,new_data)

        self.set_column_dict(new_column_dict)

class DataCurveSequence(object):

    def __init__(self,data_curves = list()):

        self.data_curves = data_curves

    def add_data_curve(self,data_curve):

        self.data_curves.append(data_curve)





        
