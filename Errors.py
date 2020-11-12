class InputTypeError(Exception): 
    def __init__(self, message="Error in the type of input file.Currently supported formats are only in csv and excel."):
        self.message = message
        super().__init__(self.message)

class InputFormatError(Exception):
    def __init__(self, columns, message="Error in number of columns in the input file."):
        self.cols = columns
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        columns = ','.join(self.cols)
        return f'{self.message} -> {columns}'


class EmptyInputError(Exception):
    def __init__(self, message='Failed to import any data.'):
        self.message = message
        super().__init__(self.message)


class NoneTypeError(Exception):
    def __init__(self, variable, message="Passed variable is None.Cannot be None"):
        self.message = variable + " : " + message
        super().__init__(self.message)


class MatchTypeError(Exception):
    def __init__(self, variable, message="Input type for passed config variable :'matchtype'"):
        self.message = variable + " : " + message
        super().__init__(self.message)


class InputColumnError(Exception):
    def __init__(self, file_type=None, input_col_numbers=None, desired_col_numbers=None):
        self.input_col_numbers = input_col_numbers
        self.output_col_numbers = desired_col_numbers
        self.file_type = file_type
        self.message = ("Input format Error.Number of columns in the input file is " + str(self.input_col_numbers)
                        + " .Desired number of columns are " + str(self.output_col_numbers) + ". Check input File."
                                                                                              "Filetype : " +
                        self.file_type)
        super().__init__(self.message)
