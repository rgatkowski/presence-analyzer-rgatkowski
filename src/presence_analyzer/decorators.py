# -*- coding: utf-8 -*-
"""
All decorators.
"""

import datetime
from threading import Lock


class decoratorCache(object):
    '''
    Read date from cache or from file.
    '''
    data = {}
    last_time = None

    def __init__(self, arg1 = 600):
        """
        Set arg1 and last time value.
        """
        self.last_time = datetime.datetime(1970,1,1)
        self.arg1 = arg1

    def __call__(self, func):
        """
        Execute function.
        """
        def wrapped_f(*args):
            now = datetime.datetime.now()
            with Lock():
                if (now - self.last_time).seconds > self.arg1:
                    self.last_time = datetime.datetime.now()
                    self.data = func()
                return self.data
        return wrapped_f