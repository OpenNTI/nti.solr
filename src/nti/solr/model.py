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

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog 
from nti.solr.interfaces import ICoreDocument

from nti.schema.interfaces import find_most_derived_interface

@interface.implementer(ICoreCatalog)
class CoreCatalog(object):
    
    def add(self, value):
        doc_id = IIDValue(value).value()
        return self.index_doc(doc_id, value)

    def index_doc(self, doc_id, alue):
        find_most_derived_interface(self, ICoreDocument)

    def remove(self, value):
        if isinstance(value, int):
            value = str(int)
        elif not isinstance(value, six.string_types):
            value = IIDValue(value).value()
        return self.unindex_doc(value)
    
    def unindex_doc(self, doc_id):
        pass
