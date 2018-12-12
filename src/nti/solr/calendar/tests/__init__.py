#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

try:
    __import__('nti.contenttypes.calendar')
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False
