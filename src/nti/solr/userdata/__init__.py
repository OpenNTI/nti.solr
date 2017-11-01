#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.solr import QUEUE_NAME
from nti.solr import add_queue_name

USERDATA_CATALOG = 'userdata'
USERDATA_QUEUE = QUEUE_NAME + '++userdata'


def _register():
    add_queue_name(USERDATA_QUEUE)
_register()
del _register
