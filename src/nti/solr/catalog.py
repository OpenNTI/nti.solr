#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
from collections import Mapping

import pysolr

from zope import component
from zope import interface

from zope.event import notify

from zope.intid.interfaces import IIntIds

from zope.schema.interfaces import IDatetime

import BTrees

from nti.externalization.externalization import to_external_object

from nti.property.property import Lazy
from nti.property.property import alias
from nti.property.property import readproperty

from nti.solr import NTI_CATALOG
from nti.solr import primitive_types

from nti.solr.interfaces import ISOLR
from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ITextField
from nti.solr.interfaces import IIntIdValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ICoreDocument
from nti.solr.interfaces import ISuggestField
from nti.solr.interfaces import ObjectIndexedEvent
from nti.solr.interfaces import ObjectUnindexedEvent

from nti.solr.lucene import lucene_escape
from nti.solr.lucene import is_phrase_search

from nti.solr.query import hl_snippets
from nti.solr.query import hl_useFastVectorHighlighter

from nti.solr.schema import SolrDatetime

from nti.solr.utils import normalize_key
from nti.solr.utils import object_finder

from nti.zope_catalog.catalog import ResultSet

@interface.implementer(ICoreCatalog)
class CoreCatalog(object):

	__parent__ = None
	__name__ = alias('name')

	skip = False
	max_rows = 500
	auto_commit = True
	return_fields = ('id', 'score')

	name = u'Objects'
	document_interface = ICoreDocument

	family = BTrees.family64

	_OR_ = u' OR '
	_AND_ = u' AND '

	def __init__(self, core=NTI_CATALOG, name=None, client=None, auto_commit=None):
		self.core = core
		if name is not None:
			self.name = name
		if client is not None:
			self.client = client
		if auto_commit is not None:
			self.auto_commit = bool(auto_commit)

	@readproperty
	def client(self):
		config = component.getUtility(ISOLR)
		url = config.url + '/%s' % self.core
		return pysolr.Solr(url, timeout=config.timeout)

	# index methods

	def add(self, value, commit=None, event=True):
		adapted = IIDValue(value, None)
		doc_id = adapted.value() if adapted is not None else None
		if doc_id:
			return self.index_doc(doc_id, value, commit=commit, event=event)
		return False

	def _do_index(self, doc_id, document, commit=True):
		ext_obj = to_external_object(document, name='solr')
		ext_obj['id'] = doc_id
		self.client.add([ext_obj], commit=commit)

	def index_doc(self, doc_id, value, commit=None, event=True):
		document = self.document_interface(value, None)
		commit = self.auto_commit if commit is None else commit
		if document is not None:
			self._do_index(doc_id, document, commit=commit)
			if event:
				notify(ObjectIndexedEvent(value, doc_id))
			return True
		return False

	def remove(self, value, commit=None, event=True):
		if isinstance(value, int):
			value = str(int)
		elif not isinstance(value, six.string_types):
			adapted = IIDValue(value, None)
			value = adapted.value() if adapted is not None else None
		if value:
			return self.unindex_doc(value, commit=commit, event=event)
		return False

	def _do_unindex(self, doc_id, commit=None):
		commit = self.auto_commit if commit is None else commit
		self.client.delete(id=doc_id, commit=commit)

	def unindex_doc(self, doc_id, commit=None, event=True):
		self._do_unindex(doc_id, commit)
		obj = object_finder(doc_id)  # may be None
		if event and obj is not None:
			notify(ObjectUnindexedEvent(obj, doc_id))
		return obj

	def clear(self, commit=None):
		commit = self.auto_commit if commit is None else commit
		self.client.delete(q='*:*', commit=commit)
	reset = clear

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

	def _fq_from_catalog_query(self, query):
		fq = {}
		for name, value in query.items():
			if name not in self.document_interface:
				continue
			if isinstance(value, tuple) and len(value) == 2:
				if value[0] == value[1]:
					value = {'any_of': (value[0],)}
				else:
					value = {'between': value}
			elif isinstance(value, primitive_types):
				value = {'any_of': (value,)}
			__traceback_info__ = name, value
			assert isinstance(value, Mapping) and len(value) == 1, 'Invalid field query'
			for k, v in value.items():
				if k == 'any_of':
					fq[name] = "(%s)" % self._OR_.join(lucene_escape(x) for x in v)
				elif k == 'all_of':
					fq[name] = "(%s)" % self._AND_.join(lucene_escape(x) for x in v)
				elif k == 'between':
					# TODO: Convert to date
					fq[name] = "[%s TO %s]" % (lucene_escape(v[0]), lucene_escape(v[1]))
		return fq

	def _bulild_from_catalog_query(self, query):
		fq = self._fq_from_catalog_query(query)
		return ('*:*', fq, {'fl':','.join(self.return_fields)})

	def apply(self, query):
		if isinstance(query, primitive_types):
			query = str(query) if isinstance(query, six.string_types) else query
			term, fq, params = query, {}, {'fl':','.join(self.return_fields)}
		else:
			term, fq, params = self._bulild_from_catalog_query(query)
		# prepare solr params
		fq_query = ['%s:%s' % (name, value) for name, value in fq.items()]
		if fq_query:
			params['fq'] = self._AND_.join(fq_query)
		# search
		intids = component.getUtility(IIntIds) 
		result = self.family.IF.BTree()
		for hit in self.client.search(term, **params):
			uid = None
			try:
				score = hit['score'] or 1.0
				uid = int(normalize_key(hit['id']))
			except KeyError:
				continue
			except (ValueError, TypeError):
				obj = self.get_object(hit['id'], intids)
				adapted = IIntIdValue(obj, None) # get intid
				uid = adapted.value() if adapted is not None else None
			if uid is not None and uid not in result:
				result[uid] = score 
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

	# content search / ISearcher.search

	@Lazy
	def text_fields(self):
		result = []
		for name, field in self.document_interface.namesAndDescriptions(all=True):
			if ITextField.providedBy(field):
				result.append(name)
		return result

	def _fq_from_search_query(self, query, document_interface=None):
		fq = {}
		document_interface = document_interface or self.document_interface
		for name, value in query.items():
			if name not in document_interface:
				continue
			field = document_interface[name]
			if isinstance(value, tuple) and len(value) == 2:  # range
				if IDatetime.providedBy(field):
					value = [SolrDatetime.toUnicode(x) for x in value]
				fq[name] = "[%s TO %s]" % (lucene_escape(value[0]), lucene_escape(value[1]))
			elif isinstance(value, (list, tuple, set)) and value:  # OR list
				fq[name] = "(%s)" % self._OR_.join(lucene_escape(x) for x in value)
			else:
				fq[name] = lucene_escape(str(value))
		return fq

	def _params_from_search_query(self, query, text_fields=None, return_fields=None):
		params = {}
		text_fields = text_fields or self.text_fields
		if text_fields and query.applyHighlights:
			params['hl'] = 'true'
			params['hl.fl'] = ','.join(text_fields)
			if hl_useFastVectorHighlighter(query):
				params['hl.useFastVectorHighlighter'] = 'true'
			params['hl.snippets'] = hl_snippets(query)
		# return fields
		return_fields = return_fields or self.return_fields
		params['fl'] = ','.join(return_fields)
		# batching
		batchSize = getattr(query, 'batchSize', None)
		batchStart = getattr(query, 'batchStart', None)
		if batchStart is not None and batchSize:
			params['start'] = str(batchStart)
			params['rows'] = str(batchSize)
		else:
			params['rows'] = str(self.max_rows)  # default number of rows
		return params

	def _build_term_from_search_query(self, query, text_fields=None):
		text_fields = text_fields or self.text_fields
		term = lucene_escape(query.term) if not is_phrase_search(query.term) else query.term
		if text_fields:  # search all text fields
			term = "(%s)" % self._OR_.join('%s:%s' % (name, term) for name in text_fields)
		return term

	def _build_from_search_query(self, query, text_fields=None, return_fields=None):
		term = self._build_term_from_search_query(query, text_fields)
		# filter query
		fq = self._fq_from_search_query(query)
		# parameters
		params = self._params_from_search_query(query, text_fields, return_fields)
		# query-term, filter-query, params
		return (term, fq, params)

	def _prepare_solr_query(self, term, fq, params):
		fq_query = ['%s:%s' % (name, value) for name, value in fq.items()]
		if fq_query:
			params['fq'] = self._AND_.join(fq_query)
		return term, params

	def search(self, query, *args, **kwargs):
		term, fq, params = self._build_from_search_query(query)
		term, params = self._prepare_solr_query(term, fq, params)
		return self.client.search(term, **params)

	# content search / ISearcher.suggest

	@Lazy
	def suggest_fields(self):
		result = []
		for name, field in self.document_interface.namesAndDescriptions(all=True):
			if ISuggestField.providedBy(field):
				result.append(name)
		return result

	def _prepare_solr_suggest(self, query):
		params = {}
		limit = getattr(query, 'limit', None)
		if limit:
			limit['terms.limit'] = limit
		return params
	
	def suggest(self, query, fields=None, *args, **kwargs):
		suggest_fields = fields or self.suggest_fields
		params = self._prepare_solr_suggest(query)
		if suggest_fields:
			return self.client.suggest_terms(suggest_fields, query.term, **params)

	def delete(self, uid=None, q=None, commit=True):
		return self.client.delete(id=uid, q=q, commit=commit)
