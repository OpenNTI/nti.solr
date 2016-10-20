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

QUEUE_NAMES = (USERDATA_QUEUE, ENTITIES_QUEUE)

ENTITIES_CATALOG = 'entities'  
USERDATA_CATALOG = 'userdata'
  
def get_factory():
    return component.getUtility(ISOLRQueueFactory)
