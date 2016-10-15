#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import interface

from zope.event import notify

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog 
from nti.solr.interfaces import ObjectIndexedEvent
from nti.solr.interfaces import ObjectUnindexedEvent

from nti.solr.utils import object_finder

@interface.implementer(ICoreCatalog)
class CoreCatalog(object):
    
    def add(self, value):
        doc_id = IIDValue(value).value()
        return self.index_doc(doc_id, value)

    def index_doc(self, doc_id, value):
        # TODO: call SOLR
        notify(ObjectIndexedEvent(value))

    def remove(self, value):
        if isinstance(value, int):
            value = str(int)
        elif not isinstance(value, six.string_types):
            value = IIDValue(value).value()
        return self.unindex_doc(value)
    
    def unindex_doc(self, doc_id):
        # TODO: call SOLR
        obj = object_finder(doc_id)
        if obj is not None:
            notify(ObjectUnindexedEvent(obj))

    def clear(self):
        raise NotImplementedError()
