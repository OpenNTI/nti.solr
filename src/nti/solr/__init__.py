#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

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
ASSETS_CATALOG = NTI_CATALOG
COURSES_CATALOG = NTI_CATALOG
ENTITIES_CATALOG = NTI_CATALOG
USERDATA_CATALOG = NTI_CATALOG
EVALUATIONS_CATALOG = NTI_CATALOG
TRANSCRIPTS_CATALOG = NTI_CATALOG
CONTENT_UNITS_CATALOG = NTI_CATALOG

primitive_types = six.string_types + (Number,)

# ## from IPython.core.debugger import Tracer; Tracer()()

def get_factory():
	return component.getUtility(ISOLRQueueFactory)
