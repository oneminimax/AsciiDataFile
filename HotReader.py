class HotReader():
    def __init__(self,reader,file_path):

        self.reader = reader
        self.file_path = file_path

        self.data_container = self.reader.read(file_path)

    def read_data_line(self):

        good_line, new_data = self.reader._read_data_line()
        if good_line:
            self.data_container.add_data_point(new_data)

        return good_line

    def get_file_path(self):

        return self.file_path