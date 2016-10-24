#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import urllib

import pysolr

from zope import component
from zope import interface

from zope.event import notify

from zope.location.interfaces import IContained

from zope.schema.interfaces import IDatetime

from nti.externalization.externalization import to_external_object

from nti.property.property import alias, Lazy
from nti.property.property import readproperty

from nti.solr.interfaces import ISOLR
from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ITextField
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ICoreDocument
from nti.solr.interfaces import ObjectIndexedEvent
from nti.solr.interfaces import ObjectUnindexedEvent

from nti.solr.schema import SolrDatetime

from nti.solr.utils import object_finder

@interface.implementer(ICoreCatalog, IContained)
class CoreCatalog(object):

	__parent__ = None
	__name__ = alias('name')

	auto_commit = True
	document_interface = ICoreDocument

	def __init__(self, name, client=None, auto_commit=None):
		self.name = name
		if client is not None:
			self.client = client
		if auto_commit is not None:
			self.auto_commit = bool(auto_commit)

	@readproperty
	def client(self):
		config = component.getUtility(ISOLR)
		url = config.url + '/%s' % self.name
		return pysolr.Solr(url, timeout=config.timeout)

	# index methods

	def add(self, value, commit=None):
		adapted = IIDValue(value, None)
		doc_id = adapted.value() if adapted is not None else None
		if doc_id:
			return self.index_doc(doc_id, value, commit=commit)
		return False

	def index_doc(self, doc_id, value, commit=None):
		document = self.document_interface(value, None)
		commit = self.auto_commit if commit is None else commit
		if document is not None:
			ext_obj = to_external_object(document, name='solr')
			ext_obj['id'] = doc_id
			self.client.add([ext_obj], commit=commit)
			notify(ObjectIndexedEvent(value, doc_id))
			return True
		return False

	def remove(self, value, commit=None):
		if isinstance(value, int):
			value = str(int)
		elif not isinstance(value, six.string_types):
			adapted = IIDValue(value, None)
			value = adapted.value() if adapted is not None else None
		if value:
			return self.unindex_doc(value, commit=commit)
		return False

	def _do_unindex(self, doc_id, commit=None):
		commit = self.auto_commit if commit is None else commit
		self.client.delete(id=doc_id, commit=commit)

	def unindex_doc(self, doc_id, commit=None):
		self._do_unindex(doc_id, commit)
		obj = object_finder(doc_id) # may be None
		if obj is not None:
			notify(ObjectUnindexedEvent(obj, doc_id))
		return obj

	def clear(self, commit=None):
		commit = self.auto_commit if commit is None else commit
		self.client.delete(q='*:*', commit=commit)

	def get_object(self, doc_id):
		result = object_finder(doc_id)
		if result is None:
			logger.debug('Could not find object with id %r' % doc_id)
			try:
				self._do_unindex(doc_id, False)
			except Exception:
				pass
		return result
	
	@Lazy
	def _text_fields(self):
		result = []
		for name, field in self.document_interface.namesAndDescriptions(all=True):
			if ITextField.providedBy(field):
				result.append(name)
		return result

	def _build(self, query):
		term = query.term
		fq = dict()
		params = dict()
		text_fields = self._text_fields
		for name, value in query.items():
			if name not in self.document_interface:
				continue
			field = self.document_interface[name]
			if isinstance(value, tuple) and len(value) == 2: # range
				if IDatetime.providedBy(field):
					value = [SolrDatetime.toUnicode(x) for x in value]
				fq[name] = "[%s TO %s]" % (value[0], value[1])
			elif isinstance(value, (list, tuple, set)) and value: # OR list
				fq[name] = "+(%s)" % ' '.join(value)
			else:
				fq[name] = str(value)
		if text_fields and query.applyHighlights:
			params['hl'] = 'true'
			params['hl.snippets'] = '2'
			params['hl.fl'] = ','.join(text_fields)
			params['hl.useFastVectorHighlighter'] = 'true'
		# alway return id and core
		params['fl'] = 'id,score'
		# query-term, filter-query, params
		return term, urllib.urlencode(fq), params

	def apply(self, query):
		pass
