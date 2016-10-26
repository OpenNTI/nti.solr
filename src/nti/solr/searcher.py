#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import copy
from itertools import chain

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIds

from nti.contentsearch.interfaces import ISearcher
from nti.contentsearch.interfaces import ISearchQuery

from nti.contentsearch.search_hits import SearchHit
from nti.contentsearch.search_results import _SearchResults as SearchResults

from nti.contenttypes.presentation import AUDIO_MIMETYES
from nti.contenttypes.presentation import VIDEO_MIMETYES
from nti.contenttypes.presentation import TIMELINE_MIMETYES
from nti.contenttypes.presentation import RELATED_WORK_REF_MIMETYES

from nti.dataserver.interfaces import IUser

from nti.property.property import Lazy

from nti.solr import ASSETS_CATALOG
from nti.solr import COURSES_CATALOG
from nti.solr import ENTITIES_CATALOG
from nti.solr import USERDATA_CATALOG
from nti.solr import EVALUATIONS_CATALOG
from nti.solr import TRANSCRIPTS_CATALOG
from nti.solr import CONTENT_UNITS_CATALOG

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IContainerIdValue
from nti.solr.interfaces import ILastModifiedValue

CONTENT_MIME_TYPE = u'application/vnd.nextthought.content'
BOOK_CONTENT_MIME_TYPE = u'application/vnd.nextthought.bookcontent'

AUDIO_TRANSCRIPT_MIME_TYPE = u'application/vnd.nextthought.audiotranscript'
VIDEO_TRANSCRIPT_MIME_TYPE = u'application/vnd.nextthought.videotranscript'

COURSE_MIME_TYPE = u'application/vnd.nextthought.courses.courseinstance'
CATALOG_ENTRY_MIME_TYPE = u'application/vnd.nextthought.courses.coursecataloglegacyentry'

USER_MIME_TYPE = u'application/vnd.nextthought.user'
COMMUNITY_MIME_TYPE = u'application/vnd.nextthought.community'
DFL_MIME_TYPE = u'application/vnd.nextthought.dynamicfriendslist'
FRIEND_LISTS_MIME_TYPE = u'application/vnd.nextthought.friendslist'

MIME_TYPE_CATALOG_MAP = {
	# content
	CONTENT_MIME_TYPE: CONTENT_UNITS_CATALOG,
	BOOK_CONTENT_MIME_TYPE: CONTENT_UNITS_CATALOG,
	# transcripts
	AUDIO_TRANSCRIPT_MIME_TYPE: TRANSCRIPTS_CATALOG,
	VIDEO_TRANSCRIPT_MIME_TYPE: TRANSCRIPTS_CATALOG,
	# courses
	COURSE_MIME_TYPE: COURSES_CATALOG,
	CATALOG_ENTRY_MIME_TYPE: COURSES_CATALOG,
	# entities
	DFL_MIME_TYPE: ENTITIES_CATALOG,
	USER_MIME_TYPE: ENTITIES_CATALOG,
	COMMUNITY_MIME_TYPE: ENTITIES_CATALOG,
	FRIEND_LISTS_MIME_TYPE: ENTITIES_CATALOG,
}
# assets
for m in chain(AUDIO_MIMETYES, VIDEO_MIMETYES, RELATED_WORK_REF_MIMETYES, TIMELINE_MIMETYES):
	MIME_TYPE_CATALOG_MAP[m] = ASSETS_CATALOG
# evaluations
try:
	from nti.assessment.interfaces import ALL_EVALUATION_MIME_TYPES
	for m in ALL_EVALUATION_MIME_TYPES:
		MIME_TYPE_CATALOG_MAP[m] = EVALUATIONS_CATALOG
except ImportError:
	pass

@component.adapter(IUser)
@interface.implementer(ISearcher)
class _SOLRSearcher(object):

	def __init__(self, entity=None):
		self.entity = entity

	def registered_catalogs(self):
		return {k:v for k, v in component.getUtilitiesFor(ICoreCatalog)}

	@Lazy
	def intids(self):
		return component.getUtility(IIntIds)

	@classmethod
	def query_search_catalogs(query):
		if query.searchOn:
			catalogs = set()
			for m in query.searchOn:
				# look for a mimeType catalog utility
				catalog = component.queryUtility(ICoreCatalog, name=m)
				if catalog is None:  # use mapper
					catalog = MIME_TYPE_CATALOG_MAP.get(m)
				if catalog is None:  # defaults to userdata
					catalog = component.queryUtility(ICoreCatalog, name=USERDATA_CATALOG)
				catalogs.add(catalog)
			catalogs.discard(None)
		else:
			catalogs = tuple(catalogs.values())
		return catalogs

	def _get_search_hit(self, catalog, result):
		try:
			uid = result['id']
			obj = catalog.get_object(uid, self.intids)
			if obj is None:
				return None
			hit = SearchHit()
			obj = hit.Target = obj  # TODO: transformer if required
			hit.Score = result['score']
			hit.ID = IIDValue(obj).value() or uid
			# add common field hit
			for value_interface, name in ((INTIIDValue, 'NTIID'),
										  (ICreatorValue, 'Creator'),
										  (IMimeTypeValue, 'TargetMimeType')
										  (IContainerIdValue, 'ContainerId'),
										  (ILastModifiedValue, 'lastModified'),):
				adapted = value_interface(obj, None)
				if adapted is not None:
					value = adapted.value()
					setattr(hit, name, value)
			# hit is ready
			return hit
		except (ValueError, TypeError, KeyError):
			pass
		return None

	def search(self, query, *args, **kwargs):
		result = []
		query = ISearchQuery(query)
		for catalog in self.query_search_catalogs(query):
			q = copy.deepcopy(query)
			solr_results = catalog.search(q, *args, **kwargs)
			search_results = SearchResults()
			for r in solr_results:
				hit = self._get_search_hit(catalog, r)
				if hit is not None:
					search_results.add(hit)
			result.append(search_results)
		return result
