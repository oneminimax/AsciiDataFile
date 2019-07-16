class HotReader():
    def __init__(self,reader,file_path):

        self.reader = reader
        self.file_path = file_path

        self.data_curve = self.reader.read(file_path)

    def read_data_line(self):

        good_line, new_data = self.reader._read_data_line()
        if good_line:
            self.data_curve.add_data_point(new_data)

        return good_line

    def get_file_path(self):

        return self.file_path

    def get_column_names(self):

        return self.data_curve.get_column_names()

    def get_column_units(self):

        return self.data_curve.get_column_units()

    def get_column_index(self,column_name):

        return self.reader.get_column_index(column_name)

    def get_column_by_name(self,column_name):

        return self.data_curve.get_column_by_name(column_name)