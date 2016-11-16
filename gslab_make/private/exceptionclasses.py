#! /usr/bin/env python

class CustomError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CritError(CustomError):
    pass

class SyntaxError(CustomError):
    pass

class LogicError(CustomError):
    pass