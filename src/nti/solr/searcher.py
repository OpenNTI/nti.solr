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

from nti.contentsearch.interfaces import ISearchQuery
from nti.contentsearch.interfaces import IResultTransformer

from nti.contentsearch.search_hits import SearchHit
from nti.contentsearch.search_fragments import SearchFragment
from nti.contentsearch.search_results import _SearchResults as SearchResults

from nti.dataserver.interfaces import IUser

from nti.externalization.interfaces import LocatedExternalList

from nti.property.property import Lazy

from nti.solr import USERDATA_CATALOG

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import ISOLRSearcher
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IContainerIdValue
from nti.solr.interfaces import ILastModifiedValue

from nti.solr.utils import MIME_TYPE_CATALOG_MAP

from nti.solr.utils import normalize_field

@component.adapter(IUser)
@interface.implementer(ISOLRSearcher)
class _SOLRSearcher(object):

	HIT_FIELDS = ((INTIIDValue, 'NTIID'),
				  (ICreatorValue, 'Creator'),
				  (IMimeTypeValue, 'TargetMimeType'),
				  (IContainerIdValue, 'ContainerId'),
				  (ILastModifiedValue, 'lastModified'))

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
			obj = IResultTransformer(obj, obj)
			if obj is None:
				return None
			hit = SearchHit()
			hit.Target = obj # trxed
			hit.Score = result['score']
			hit.ID = IIDValue(obj).value() or uid
			# Fragments / Snippets
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
			# Add common field hit
			for value_interface, name in self.HIT_FIELDS:
				adapted = value_interface(obj, None)
				if adapted is not None:
					value = adapted.value()
					setattr(hit, name, value)
			# hit is ready
			return hit
		except (ValueError, TypeError, KeyError):
			logger.debug('Could not create hit for %s', result)
		return None

	def search(self, query, *args, **kwargs):
		result = LocatedExternalList()
		query = ISearchQuery(query)
		for catalog in self.query_search_catalogs(query):
			container = SearchResults(copy.deepcopy(query))
			events = catalog.search(query, *args, **kwargs)
			for event in events or ():
				hit = self._get_search_hit(catalog, event, events.highlighting)
				if hit is not None:
					container.add(hit)
			result.append(container)
		return result
