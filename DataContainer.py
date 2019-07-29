import numpy as np

from pint import UnitRegistry, set_application_registry
ureg = UnitRegistry(system = 'mks')
set_application_registry(ureg)

from scipy.interpolate import interp1d

class DataCurve(object):

    def __init__(self,*vargs,**kwargs):

        self.chunk_size = 10

        self.parameter_dict = dict()
        self.column_dict = dict()
        self.column_names = list()
        self.data_length = 0
        self.extend_data_length = 0
        self.curve_name = 'DataCurve'

        for arg in vargs:
            if isinstance(arg,DataCurve):
                self._apply_column_dict(arg.column_dict,new_curve = False)
                self._apply_parameter_dict(arg.parameter_dict,new_curve = False)

        if 'column_names' in kwargs and 'column_units_labels' in kwargs:
            self.init_columns(kwargs['column_names'],kwargs['column_units_labels'])
        else:
            for kw in kwargs:
                if hasattr(kwargs[kw],'shape'):
                    self.add_column(kw,kwargs[kw])
                else:
                    self.add_parameter(kw,kwargs[kw])

    def __getattr__(self,name):

        if name in self.column_dict:
            return self.column_dict[name]
        
        var_name = name.replace('_',' ')
        if var_name in self.column_dict:
            return self.column_dict[var_name]

    def __str__(self):

        info_str = f'{self.curve_name:s} ({self.data_length:d} data points)\n'
        if self.parameter_dict:
            for parameter_name in self.parameter_dict:
                info_str += parameter_name + ' : ' + str(self.parameter_dict[parameter_name]) + ', '
        if self.column_dict:
            for column_name in self.column_dict:
                info_str += ' ' + column_name + ' (' + str(self.column_dict[column_name].units) + ')\n'

        return info_str[:-1]

    def convert(self,new_class):

        return new_class(self)

    def init_columns(self,column_names,column_units_labels):

        for i, column_name in enumerate(column_names):
            try:
                column_units = ureg(column_units_labels[i])
            except:
                column_units = ureg('')
                Warning('Pint could not parse {0:s} to units. Column will be dimensionless')
            self.add_column(column_name,np.empty([0,])*column_units)

    def add_column(self,column_name,column_data):

        if self.data_length:
            if not len(column_data) == self.data_length:
                raise Exception('Data length must be the same')
        else:
            self.data_length = len(column_data)

        self.column_dict[column_name] = column_data
        self.column_names.append(column_name)

    def update_column(self,column_name,column_data):

        if not len(column_data) == self.data_length:
            raise Exception('Data length must be the same')

        self.column_dict[column_name] = column_data

    def rename_column(self,old_name,new_name):

        if old_name in self.column_names:
            self.column_names[self.column_names.index(old_name)] = new_name
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
            new_data = dict(zip(self.column_names,values))

        for column_name in self.column_dict:
            if not hasattr(new_data[column_name],'units'):
                new_data[column_name] = new_data[column_name]*self.column_dict[column_name].units
            else:
                new_data[column_name].ito(self.column_dict[column_name].units)
            
            self.column_dict[column_name][self.data_length] = new_data[column_name]

        self.data_length += 1

    def column_number(self):

        return len(self.column_dict)

    def _extend_chunk(self):

        for column_name in self.column_dict:
            larger_column_data = np.zeros((self.data_length+self.chunk_size,))*self.column_dict[column_name].units
            larger_column_data[:self.data_length] = self.column_dict[column_name]
            self.column_dict[column_name] = larger_column_data
        self.extend_data_length = self.data_length+self.chunk_size

    def crop(self):

        for column_name in self.column_dict:
            self.column_dict[column_name] = self.column_dict[column_name][:self.data_length]

        self.extend_data_length = self.data_length+0

    def _apply_column_dict(self,column_dict,new_curve):

        if new_curve:
            return self.__class__(**column_dict,**self.parameter_dict)
        else:
            self.set_column_dict(column_dict)

    def _apply_parameter_dict(self,parameter_dict,new_curve):

        if new_curve:
            return self.__class__(**column_dict,**self.parameter_dict)
        else:
            self.parameter_dict = parameter_dict

    def set_column_dict(self,column_dict):

        data_lengths = list()
        for column_name in column_dict:
            data_lengths.append(len(column_dict[column_name]))

        data_length = np.unique(data_lengths)
        if len(data_length) == 1:
            self.column_dict = column_dict
            self.column_names = list(column_dict.keys())
            self.data_length = data_length[0]
        else:
            raise Exception('Data length must be the same')

    def add_parameter(self,parameter_name,parameter_value):

        self.parameter_dict[parameter_name] = parameter_value

    def get_column_names(self):

        return self.column_names

    def get_column_units(self,as_string = False):

        column_units = list()

        for column_name in self.column_names:
            if as_string:
                column_units.append('{:~P}'.format(self.column_dict[column_name].units))
            else:
                column_units.append(self.column_dict[column_name].units)

        return column_units

    def get_column_by_name(self,column_name):

        return self.column_dict[column_name][:self.data_length]

    # Manipulation methods

    def equals_within_tolerance(self,column_name,value,tolerance):

        return np.abs((getattr(self,column_name) - value)) < tolerance

    def filter(self,mask,new_curve = False):

        new_column_dict = dict()
        for column_name in self.column_dict:
            new_column_dict[column_name] = getattr(self,column_name)[mask]

        return self._apply_column_dict(new_column_dict,new_curve)

    def select_value(self,column_name,value,tolerance,new_curve = False):
        
        mask = self.equals_within_tolerance(column_name,value,tolerance)
        return self.filter(mask,new_curve)

    def select_direction(self,column_name,direction,new_curve = False):

        mask = np.gradient(getattr(self,column_name).magnitude)*direction > 0
        return self.filter(mask,new_curve)

    def average_multiple_measurement(self,select_column_name,value_step,new_curve = False):

        unique_values = np.unique(np.round((self.column_dict[select_column_name].to(value_step.units)/value_step).magnitude))*value_step
        
        new_column_dict = dict()

        for column_name in self.column_dict:
            column_units = self.column_dict[column_name].units
            new_column_dict[column_name] = np.zeros(unique_values.shape)*column_units
            for i_value, value in enumerate(unique_values):
                ind = (self.column_dict[select_column_name] - value)**2 < value_step**2/2
            
                new_column_dict[column_name][i_value] = np.average(self.column_dict[column_name][ind].magnitude)*column_units

        return self._apply_column_dict(new_column_dict,new_curve)

    def y_at_x(self,x_column_name,y_column_name,x_values):

        f = interp1d(self.column_dict[x_column_name].magnitude,self.column_dict[y_column_name].magnitude,fill_value='extrapolate')

        return f(x_values.to(self.column_dict[x_column_name].units).magnitude)*self.column_dict[y_column_name].units

    def symetrize(self,x_column_name,sym_y_column_names = list(),antisym_y_column_names = list(),x_values = None,x_step = None,new_curve = False):

        if x_values is None and not x_step is None:
            x_values = self.auto_sym_x_values(x_column_name,x_step)
        elif not x_values is None and x_step is None:
            pass
        else:
            raise(ValueError('Most provide x_values or x_step'))

        new_column_dict = dict()
        for column_name in self.column_names:
            f = interp1d(getattr(self,x_column_name).magnitude,getattr(self,column_name).magnitude,fill_value='extrapolate')
            if column_name in sym_y_column_names:
                new_column_dict[column_name] = (f(x_values.magnitude) + f(-x_values.magnitude))/2 * getattr(self,column_name).units

            if column_name in antisym_y_column_names:
                new_column_dict[column_name] = (f(x_values.magnitude) - f(-x_values.magnitude))/2 * getattr(self,column_name).units
        
        return self._apply_column_dict(new_column_dict,new_curve)

    def auto_sym_x_values(self,x_column_name,x_step):

        max_x_value = np.max(np.round(getattr(self,x_column_name)/x_step))*x_step

        return np.linspace(0,max_x_value.magnitude,int(max_x_value/x_step)+1)*getattr(self,x_column_name).units


    
