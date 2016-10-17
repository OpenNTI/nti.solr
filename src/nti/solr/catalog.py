#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

import pysolr

from zope import component
from zope import interface

from zope.event import notify

from nti.property.property import readproperty

from nti.solr.interfaces import ISOLR
from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog 
from nti.solr.interfaces import ObjectIndexedEvent
from nti.solr.interfaces import ObjectUnindexedEvent

from nti.solr.utils import object_finder

@interface.implementer(ICoreCatalog)
class CoreCatalog(object):
    
    def __init__(self, name, client=None):
        self.name = name
        if client is not None:
            self.client = client

    @readproperty
    def client(self, name=u''):
        config = component.getUtility(ISOLR, name=u'')
        url = config.url + '/%s' % self.name
        self.client = pysolr.Solr(url, timeout=config.timeout)
        return self.client

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
        self.client.delete(id=doc_id)
        obj = object_finder(doc_id)
        if obj is not None:
            notify(ObjectUnindexedEvent(obj))
        return obj

    def clear(self):
        self.client.delete(q='*:*')
