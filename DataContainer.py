import numpy as np

from pint import UnitRegistry, set_application_registry
ureg = UnitRegistry(system = 'mks')
set_application_registry(ureg)

from scipy.interpolate import interp1d

class DataBag(object):
    def __init__(self,column_number,chunk_size = 10):

        self.chunk_size = chunk_size
        self.column_number = column_number
        
        self.data_bag = np.empty((self.chunk_size,self.column_number))
        self.data_point_number = 0

    def __str__(self):

        return str(self.data_bag)

    def add_data_point(self,new_data):

        if not len(new_data) == self.column_number:
            raise ValueError('New Data Length ({0:d}) is not conform to the number of data fields ({1:d}).'.format(len(new_data),self.column_number))

        if self.data_bag.shape[0] == self.data_point_number:
            self._extend_chunk()
        self.data_bag[self.data_point_number,:] = new_data
        self.data_point_number += 1
            
    def _extend_chunk(self):

        larger_data_bag = np.empty((self.data_point_number+self.chunk_size,self.column_number))
        larger_data_bag[:self.data_point_number,:] = self.data_bag
        self.data_bag = larger_data_bag

    def crop(self):

        larger_data_bag = np.empty((self.data_point_number,self.column_number))
        larger_data_bag = self.data_bag[:self.data_point_number,:]
        self.data_bag = larger_data_bag

    def to_data_curve(self,column_names,column_units):

        data_dict = dict()
        for i, column_name in enumerate(column_names):
            try:
                units = ureg.Unit(column_units[i])
                data_dict[column_name] = self.data_bag[:,i]*ureg.Unit(column_units[i])
            except:
                pass # ditch column without units                

        return DataCurve(**data_dict)



class DataCurve(object):

    def __init__(self,*vargs,**kwargs):

        self.parameter_dict = dict()
        self.column_dict = dict()
        self.column_length = 0
        self.curve_name = 'DataCurve'

        for arg in vargs:
            if isinstance(arg,DataCurve):
                self._apply_column_dict(arg.column_dict,new_curve = False)
                self._apply_parameter_dict(arg.parameter_dict,new_curve = False)

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

        info_str = '{0:s}\n'.format(self.curve_name)
        if self.parameter_dict:
            info_str += 'Parameters : \n'
            for parameter_name in self.parameter_dict:
                info_str += parameter_name + ' : ' + str(self.parameter_dict[parameter_name]) + '\n'
            info_str += ' --- ' + '\n' + 'Columns : \n'
        if self.column_dict:
            for column_name in self.column_dict:
                info_str += column_name + ' (' + str(self.column_dict[column_name].units) + ')\n'

        return info_str[:-1]

    def add_column(self,column_name,column_data):

        if self.column_length:
            if not len(column_data) == self.column_length:
                raise Exception('Data length must be the same')
        else:
            self.column_length = len(column_data)

        self.column_dict[column_name] = column_data

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

        column_lengths = list()
        for column_name in column_dict:
            column_lengths.append(len(column_dict[column_name]))

        column_length = np.unique(column_lengths)
        if len(column_length) == 1:
            self.column_dict = column_dict
            self.column_length = column_length[0]
        else:
            raise Exception('Data length must be the same')

    def add_parameter(self,parameter_name,parameter_value):

        self.parameter_dict[parameter_name] = parameter_value

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

    
