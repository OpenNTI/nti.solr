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

from nti.contentsearch.interfaces import ISearchQuery, ISearchHit

from nti.contentsearch.search_fragments import SearchFragment

try:
	from nti.contentsearch.search_results import _SearchResults as SearchResults
except ImportError:
	from nti.contentsearch.search_results import SearchResults

from nti.dataserver.interfaces import IUser

from nti.externalization.interfaces import LocatedExternalList

from nti.property.property import Lazy

from nti.solr import USERDATA_CATALOG

from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ISOLRSearcher

from nti.solr.utils import MIME_TYPE_CATALOG_MAP

from nti.solr.utils import normalize_field

@component.adapter(IUser)
@interface.implementer(ISOLRSearcher)
class _SOLRSearcher(object):

	def __init__(self, entity=None):
		self.entity = entity

	@Lazy
	def intids(self):
		return component.getUtility(IIntIds)

	def registered_catalogs(self):
		return tuple(v for _, v in component.getUtilitiesFor(ICoreCatalog))

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
			hit = component.getMultiAdapter((obj, result), ISearchHit)
			# set fragments
			fragments = list()
			snippets = highlighting.get(uid) if highlighting else None
			if snippets:
				for name, value in snippets.values():
					fragment = SearchFragment()
					fragment.field = normalize_field(name)
					fragment.matches = list(value)
					fragments.append(fragment)
			if fragments:
				hit.Fragments = fragments
			return hit
		except Exception:
			logger.debug('Could not create hit for %s', result)
		return None

	def search(self, query, *args, **kwargs):
		query = ISearchQuery(query)
		result = LocatedExternalList()
		for catalog in self.query_search_catalogs(query):
			container = SearchResults(Query=copy.deepcopy(query))
			try:
				events = catalog.search(query, *args, **kwargs)
				for event in events or ():
					hit = self._get_search_hit(catalog, event, events.highlighting)
					if hit is not None:
						container.add(hit)
				result.append(container)
			except Exception:
				logger.exception("Error while executing query %s on %s", query, catalog)
		return result
