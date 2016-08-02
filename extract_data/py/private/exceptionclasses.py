#! /usr/bin/env python

######################################################
# Define Exception Classes
######################################################	

class CustomError(Exception):

	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)	

class CritError(CustomError):
	pass
