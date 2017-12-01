#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=W0603

import six
from numbers import Number

from zope import component

from nti.solr.interfaces import ISOLRQueueFactory

QUEUE_NAME = '++etc++solr++queue'
QUEUE_NAMES = ()

NTI_CATALOG = 'nti'

DEFAULT_LANGUAGE = 'en'

primitive_types = six.string_types + (Number, bool)

_OR_ = u' OR '
_AND_ = u' AND '


def get_factory():
    return component.getUtility(ISOLRQueueFactory)


def add_queue_name(name):
    global QUEUE_NAMES
    if name not in QUEUE_NAMES:
        QUEUE_NAMES += (name,)
addQueue = add_queue_name
