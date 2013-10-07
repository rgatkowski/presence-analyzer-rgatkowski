# -*- coding: utf-8 -*-
"""
All decorators.
"""

import datetime
from threading import Lock


class DecoratorCache(object):
    '''
    Read date from cache or from file.
    '''
    data = {}
    last_time = None
    mutex = None

    def __init__(self, sec_timeout=600):
        """
        Set arg1 and last time value.
        """
        self.last_time = datetime.datetime(1970, 1, 1)
        self.sec_timeout = sec_timeout
        self.mutex = Lock()

    def __call__(self, func):
        """
        Execute function.
        """

        def wrapped_f():
            now = datetime.datetime.now()
            with self.mutex:
                if (now - self.last_time).total_seconds() > self.sec_timeout:
                    self.last_time = datetime.datetime.now()
                    self.data = func()
                return self.data
        return wrapped_f
