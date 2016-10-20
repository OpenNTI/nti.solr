#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.solr.interfaces import ISOLRQueueFactory

QUEUE_NAME = '++etc++solr++queue'

ENTITIES_QUEUE = QUEUE_NAME + '++entities'
USERDATA_QUEUE = QUEUE_NAME + '++userdata'
EVALUATIONS_QUEUE = QUEUE_NAME + '++evaluations'

QUEUE_NAMES = (USERDATA_QUEUE, ENTITIES_QUEUE, EVALUATIONS_QUEUE)

ENTITIES_CATALOG = 'entities'  
USERDATA_CATALOG = 'userdata'
EVALUATIONS_CATALOG = 'evaluations'

### from IPython.core.debugger import Tracer; Tracer()()

def get_factory():
    return component.getUtility(ISOLRQueueFactory)
