
##  Implements exceptions/errors that are needed in CMD class and associated programs.
##

class Error(Exception):
    pass

class WError(Error):
    def __init__(self):
        self.msg = "W must be a positive semi-definite matrix"
    def __str__(self):
        return repr(self.msg)

class statsError(Error):
    def __init__(self):
        self.msg = "If W is an nxn matrix, then stats needs to be a nx1 vector"
    def __str__(self):
        return repr(self.msg)
    