from AsciiDataFile import DataContainer
from AsciiDataFile.Readers import DataColumnReader as Reader

import os


reader = Reader()

DC1 = reader.read('../Examples/Data/test_column.txt')
DC2 = reader.read('../Examples/Data/test_column.txt')
print(DC1)
# DC1.rename_column('X','Z')
# print(DC1)
# DC1.add_data_point([0,1])
# 
# DC1.filter(DC1.get_column('Y')>0)
# DC1.select_value('Y',0.9,0.1)
# DC1.select_direction('Y',1)
# DC1.average_multiple_measurement('Y',0.1)
# y = DC1.y_at_x('X','Y',[0.2])
# print(y)

# DC1.symetrize('Y',[],['X','Y'],x_step = 0.1)
# sym_y = DC1.auto_sym_x_values('Y',0.1)
# print(sym_y)
DC1.append(DC2)
DC1.sort_by('X')
print(DC1)