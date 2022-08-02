#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/debuggers.py

import logging

logger = logging.getLogger(__name__)

class Debugger(object):
    """ Debug a method and return it back"""

    enabled = False

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if self.enabled:
            logger.debug(f'Entering : {self.func.__name__}')
            logger.debug(f'args, kwargs : {args, kwargs}')
            logger.debug(f'{self.func.__name__} returned : {self.func(*args, **kwargs)}')

        return self.func(*args, **kwargs)