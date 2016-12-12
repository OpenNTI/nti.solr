#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import copy

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIds

from nti.contentsearch.interfaces import ISearchHit
from nti.contentsearch.interfaces import ISearchQuery 

from nti.contentsearch.search_fragments import SearchFragment

try:
	from nti.contentsearch.search_results import SearchResults
	from nti.contentsearch.search_results import SuggestResults
except ImportError:
	from nti.contentsearch.search_results import _SearchResults as SearchResults
	from nti.contentsearch.search_results import _SuggestResults as SuggestResults

from nti.dataserver.interfaces import IUser

from nti.property.property import Lazy

from nti.solr import USERDATA_CATALOG

from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ISOLRSearcher

from nti.solr.utils import MIME_TYPE_CATALOG_MAP

from nti.solr.utils import normalize_field
from nti.solr.utils import gevent_spawn

@component.adapter(IUser)
@interface.implementer(ISOLRSearcher)
class _SOLRSearcher(object):

	def __init__(self, entity=None, parallel_search=False):
		self.entity = entity
		self.parallel_search = False

	@Lazy
	def intids(self):
		return component.getUtility(IIntIds)

	def registered_catalogs(self):
		return tuple(v for _, v in component.getUtilitiesFor(ICoreCatalog))

	def _query_clone(self, query):
		clone = copy.deepcopy(query)
		clone.term = clone.term.lower()
		return clone

	def query_search_catalogs(self, query):
		if query.searchOn:
			catalogs = set()
			for mimeType in query.searchOn:
				# look for a mimeType catalog utility
				catalog = component.queryUtility(ICoreCatalog, name=mimeType)
				if catalog is None: # use mapper
					name = MIME_TYPE_CATALOG_MAP.get(mimeType) or u''
					catalog = component.queryUtility(ICoreCatalog, name=name)
				if catalog is None: # defaults to userdata
					catalog = component.queryUtility(ICoreCatalog, name=USERDATA_CATALOG)
				catalogs.add(catalog)
			catalogs.discard(None)
		else:
			catalogs = self.registered_catalogs()
		return catalogs

	def _get_search_hit(self, catalog, result, highlighting=None):
		try:
			uid = result['id']
			obj = catalog.get_object(uid, self.intids)
			if obj is None:
				return None
			hit = component.queryMultiAdapter((obj, result), ISearchHit)
			if hit is None:
				return None
			# set fragments
			fragments = list()
			snippets = highlighting.get(uid) if highlighting else None
			if snippets:
				for name, value in snippets.items():
					fragment = SearchFragment()
					fragment.__parent__ = hit # ownership
					fragment.Field = normalize_field(name)
					fragment.Matches = list(value)
					fragments.append(fragment)
			if fragments:
				hit.Fragments = fragments
			return hit
		except Exception as e:
			logger.debug('Could not create hit for %s. %s', result, e)
		return None

	def _do_search(self, catalog, query, *args, **kwargs):
		try:
			events = catalog.search(query, *args, **kwargs)
			for event in events or ():
				hit = self._get_search_hit(catalog, event, events.highlighting)
				if hit is not None:
					yield hit, events.hits
		except Exception:
			logger.exception("Error while executing query %s on %s", query, catalog)
			
	def search(self, query, *args, **kwargs):
		numFound = 0
		generators = []
		query = ISearchQuery(query)
		clone = self._query_clone(query)
		catalogs = self.query_search_catalogs(query)
		parallel_search = self.parallel_search and len(catalogs) > 1
		result = SearchResults(Name="Hits", Query=query)
		for catalog in self.query_search_catalogs(query):
			if catalog.skip:
				continue
			if parallel_search:
				generators.append(gevent_spawn(func=self._do_search,
											   catalog=catalog,
											   query=clone))
			else:
				generators.append(self._do_search(catalog, clone))
		# collect valeus
		for generator in generators:
			values = generator.get() if parallel_search else generator
			for hit, found in values:
				result.add(hit)
		numFound += found
		result.NumFound = numFound
		return result
	
	def _get_suggestions(self, catalog, events):
		result = set()
		for hits in events.values():
			result.update(x for x,_ in hits)		
		return result
	
	def suggest(self, query, *args, **kwargs):
		query = ISearchQuery(query)
		clone = self._query_clone(query)
		result = SuggestResults(Name="Suggestions", Query=query)
		for catalog in self.query_search_catalogs(query):
			try:
				events = catalog.suggest(clone)
				if events: # may be None
					result.extend(self._get_suggestions(catalog, events))
			except Exception:
				logger.exception("Error while executing query %s on %s", query, catalog)
		return result
