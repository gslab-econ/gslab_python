class BadExecutableError(Exception):
	def __init__(self, message = ''):
		print 'Error: ' + message

class BadExtensionError(Exception):
	def __init__(self, message = ''):
		print 'Error: ' + message

class LFSError(Exception):
	def __init__(self, message = ''):
		print 'Error: ' + message

class ReleaseOptionsError(Exception):
    def __init__(self, message = ''):
        print 'Error: ' + message
