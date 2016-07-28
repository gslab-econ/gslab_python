class AuthenticationError(Exception):
    def __init__(self, value):
        self._value = value
    def __str__(self):
        return repr(self._value)

class NullInputException(Exception):
    def __init__(self, value):
        self._value = value
    def __str__(self):
        return repr(self._value)

class IllegalStateException(Exception):
    def __init__(self, value):
        self._value = value
    def __str__(self):
        return repr(self._value)