#! /usr/bin/env python

import unittest

loader = unittest.TestLoader()
tests = loader.discover('.')
testRunner = unittest.TextTestRunner(verbosity=2)
testRunner.run(tests)
