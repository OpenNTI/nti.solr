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
from numbers import Number
from collections import Mapping

import pysolr

from zope import component
from zope import interface

from zope.catalog.catalog import ResultSet

from zope.event import notify

from zope.intid.interfaces import IIntIds

from zope.location.interfaces import IContained

from zope.schema.interfaces import IDatetime

import BTrees

from nti.externalization.externalization import to_external_object

from nti.externalization.interfaces import LocatedExternalDict

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

_primitive_types = six.string_types + (Number,)

@interface.implementer(ICoreCatalog, IContained)
class CoreCatalog(object):

	__parent__ = None
	__name__ = alias('name')

	auto_commit = True
	return_fields = ('id', 'score')
	document_interface = ICoreDocument

	family = BTrees.family64

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
		obj = object_finder(doc_id)  # may be None
		if obj is not None:
			notify(ObjectUnindexedEvent(obj, doc_id))
		return obj

	def clear(self, commit=None):
		commit = self.auto_commit if commit is None else commit
		self.client.delete(q='*:*', commit=commit)

	def get_object(self, doc_id, intids=None):
		result = object_finder(doc_id, intids)
		if result is None:
			logger.debug('Could not find object with id %r' % doc_id)
			try:
				self._do_unindex(doc_id, False)
			except Exception:
				pass
		return result

	# zope catalog

	def _bulild_from_catalog_query(self, query):
		fq = {}
		for name, value in query.items():
			if name not in self.document_interface:
				continue
			if isinstance(value, tuple) and len(value) == 2:
				if value[0] == value[1]:
					value = {'any_of': (value[0],)}
				else:
					value = {'between': value}
			elif isinstance(value, _primitive_types):
				value = {'any_of': (value,)}
			__traceback_info__ = name, value
			assert isinstance(value, Mapping) and len(value) == 1, 'Invalid field query'
			for k, v in value.items():
				if k == 'any_of':
					fq[k] = "+(%s)" % ' '.join(v)
				elif k == 'all_of':
					fq[k] = "(%s)" % 'AND'.join(v)
				elif k == 'between':
					fq[k] = "[%s TO %s]" % (v[0], v[1])
		# query-term, filter-query, params
		return ('*:*', fq, {'fl':','.join(self.return_fields)})

	def apply(self, query):
		if isinstance(query, _primitive_types):
			query = str(query) if isinstance(query, six.string_types) else query
			term, fq, params = query, {}, {'fl':','.join(self.return_fields)}
		else:
			term, fq, params = self._bulild_from_catalog_query(query)
		# prepare solr query
		all_query = {'q': term}
		all_query.update(fq)
		q = urllib.urlencode(all_query)
		# search
		result = self.family.IF.BTree()
		for hit in self.client.search(q, **params):
			try:
				uid = int(hit['id'])
				result[uid] = hit['score']
			except (ValueError, TypeError, KeyError):
				pass
		return result

	def searchResults(self, **searchterms):
		searchterms.pop('_sort_index', None)
		limit = searchterms.pop('_limit', None)
		reverse = searchterms.pop('_reverse', False)
		results = self.apply(searchterms)
		if reverse or limit:
			results = list(results)
			if reverse:
				results.reverse()
			if limit:
				del results[limit:]
		intids = component.getUtility(IIntIds)
		results = ResultSet(results, intids)
		return results

	# content search / ISearcher

	@Lazy
	def _text_fields(self):
		result = []
		for name, field in self.document_interface.namesAndDescriptions(all=True):
			if ITextField.providedBy(field):
				result.append(name)
		return result

	def _build_from_search_query(self, query):
		fq = dict()
		params = dict()
		term = query.term
		text_fields = self._text_fields
		# filter query
		for name, value in query.items():
			if name not in self.document_interface:
				continue
			field = self.document_interface[name]
			if isinstance(value, tuple) and len(value) == 2:  # range
				if IDatetime.providedBy(field):
					value = [SolrDatetime.toUnicode(x) for x in value]
				fq[name] = "[%s TO %s]" % (value[0], value[1])
			elif isinstance(value, (list, tuple, set)) and value:  # OR list
				fq[name] = "+(%s)" % ' '.join(value)
			else:
				fq[name] = str(value)
		# highlights
		applyHighlights = getattr(query, 'applyHighlights', False)
		if text_fields and applyHighlights:
			params['hl'] = 'true'
			params['hl.fl'] = ','.join(text_fields)
			params['hl.useFastVectorHighlighter'] = 'true'
			params['hl.snippets'] = getattr(query, 'snippets', None) or '2'
		# return fields
		params['fl'] = ','.join(self.return_fields)
		# batching
		batchSize = getattr(query, 'batchSize', None)
		batchStart = getattr(query, 'batchStart', None)
		if batchStart is not None and batchSize:
			params['start'] = str(batchStart)
			params['rows'] = str(batchSize)
		# query-term, filter-query, params
		return (term, fq, params)

	def search(self, query, *args, **kwargs):
		if isinstance(query, _primitive_types):
			d = LocatedExternalDict()
			d.term = str(query) if isinstance(query, six.string_types) else query
			query = d  # replace
		# prepare solr query
		term, fq, params = self._bulild_from_catalog_query(query)
		all_query = {'q': term}
		all_query.update(fq)
		q = urllib.urlencode(all_query)
		return self.client.search(q, **params)
