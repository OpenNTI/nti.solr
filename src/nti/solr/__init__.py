#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six
from numbers import Number

from zope import component

from nti.solr.interfaces import ISOLRQueueFactory

QUEUE_NAME = '++etc++solr++queue'

ASSETS_QUEUE = QUEUE_NAME + '++assets'
COURSES_QUEUE = QUEUE_NAME + '++courses'
ENTITIES_QUEUE = QUEUE_NAME + '++entities'
USERDATA_QUEUE = QUEUE_NAME + '++userdata'
EVALUATIONS_QUEUE = QUEUE_NAME + '++evaluations'
TRANSCRIPTS_QUEUE = QUEUE_NAME + '++transcripts'
CONTENT_UNITS_QUEUE = QUEUE_NAME + '++contentunits'

QUEUE_NAMES = (CONTENT_UNITS_QUEUE, TRANSCRIPTS_QUEUE,
               USERDATA_QUEUE, ASSETS_QUEUE, ENTITIES_QUEUE,
               EVALUATIONS_QUEUE, COURSES_QUEUE)

NTI_CATALOG = 'nti'
ASSETS_CATALOG = 'assets'
COURSES_CATALOG = 'courses'
ENTITIES_CATALOG = 'entities'
USERDATA_CATALOG = 'userdata'
EVALUATIONS_CATALOG = 'evaluations'
TRANSCRIPTS_CATALOG = 'transcripts'
CONTENT_UNITS_CATALOG = 'contentunits'

primitive_types = six.string_types + (Number, bool)

_OR_ = u' OR '
_AND_ = u' AND '


def get_factory():
    return component.getUtility(ISOLRQueueFactory)
