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

from zope.location.interfaces import IContained

from nti.externalization.externalization import to_external_object

from nti.property.property import alias
from nti.property.property import readproperty

from nti.solr.interfaces import ISOLR
from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ICoreDocument
from nti.solr.interfaces import ObjectIndexedEvent
from nti.solr.interfaces import ObjectUnindexedEvent

from nti.solr.utils import object_finder

@interface.implementer(ICoreCatalog, IContained)
class CoreCatalog(object):

	__parent__ = None
	__name__ = alias('name')

	document_interface = ICoreDocument

	def __init__(self, name, client=None):
		self.name = name
		if client is not None:
			self.client = client

	@readproperty
	def client(self):
		config = component.getUtility(ISOLR)
		url = config.url + '/%s' % self.name
		return pysolr.Solr(url, timeout=config.timeout)

	def add(self, value, commit=True):
		doc_id = IIDValue(value).value()
		return self.index_doc(doc_id, value, commit=commit)

	def index_doc(self, doc_id, value, commit=True):
		document = self.document_interface(value, value)
		ext_obj = to_external_object(document, name='solr')
		if doc_id != ext_obj.get('id'):
			ext_obj['id'] = doc_id
		self.client.add([ext_obj], commit=commit)
		notify(ObjectIndexedEvent(value, doc_id))

	def remove(self, value, commit=True):
		if isinstance(value, int):
			value = str(int)
		elif not isinstance(value, six.string_types):
			value = IIDValue(value).value()
		return self.unindex_doc(value, commit=commit)

	def unindex_doc(self, doc_id, commit=True):
		self.client.delete(id=doc_id, commit=commit)
		obj = object_finder(doc_id)  # may be None
		notify(ObjectUnindexedEvent(obj, doc_id))
		return obj

	def clear(self, commit=True):
		self.client.delete(q='*:*', commit=commit)
