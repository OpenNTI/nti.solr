#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import copy

from zope import component
from zope import interface

from zope.cachedescriptors.property import Lazy

from zope.intid.interfaces import IIntIds

from nti.contentsearch.interfaces import ISearchHit
from nti.contentsearch.interfaces import ISearchQuery

from nti.contentsearch.search_fragments import SearchFragment

from nti.dataserver.interfaces import IUser

from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ISOLRSearcher

from nti.solr.userdata import USERDATA_CATALOG

from nti.solr.utils import normalize_field
from nti.solr.utils import mimeTypeRegistry

logger = __import__('logging').getLogger(__name__)


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

    def _query_clone(self, query):
        clone = copy.deepcopy(query)
        clone.term = clone.term.lower()
        return clone

    def query_search_catalogs(self, query):
        # If search term startswith #, userdata - tag field only
        if query.searchOn:
            catalogs = set()
            for mimeType in query.searchOn:
                # look for a mimeType catalog utility
                catalog = component.queryUtility(ICoreCatalog, name=mimeType)
                if catalog is None:  # use mapper
                    name = mimeTypeRegistry.getCatalog(mimeType, '')
                    catalog = component.queryUtility(ICoreCatalog, name=name)
                if catalog is None:  # defaults to userdata
                    catalog = component.queryUtility(ICoreCatalog,
                                                     name=USERDATA_CATALOG)
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
            assert hit.ID, "search hit must have an ID"
            assert hit.Target is not None, "search hit must have an target"
            # set fragments
            fragments = list()
            snippets = highlighting.get(uid) if highlighting else None
            if snippets:
                for name, value in snippets.items():
                    fragment = SearchFragment()
                    fragment.__parent__ = hit  # ownership
                    fragment.Field = normalize_field(name)
                    fragment.Matches = list(value)
                    fragments.append(fragment)
            if fragments:
                hit.Fragments = fragments
            return hit
        except Exception as e:  # pylint: disable=broad-except
            logger.debug('Could not create hit for %s. %s', result, e)
        return None

    def _execute_search(self, catalog, term, fq, params, query=None):
        try:
            events = catalog.execute(term, fq, params, query)
            for event in events or ():
                if not catalog.filter(event, query):
                    hit = self._get_search_hit(catalog, event, events.highlighting)
                else:
                    hit = None
                # Always yield hit, even if None; it lets the caller batch
                # properly. Not sure the best way to handle this; seems like
                # we want to always return what SOLR gives us, even if None.
                # Thus, the caller can keep calling us, with incrementing
                # batches until SOLR runs out of results or the batch is filled.
                yield hit
        except Exception: # pylint: disable=broad-except
            logger.exception("Error while executing query %s", term)

    # pylint: disable=keyword-arg-before-vararg

    def search(self, query, batch_start=None, batch_size=None,
               *unused_args, **unused_kwargs):
        queries = {}
        query = ISearchQuery(query)
        catalogs = self.query_search_catalogs(query)
        # collect catalogs by core and build query triplets
        for catalog in catalogs or ():
            if catalog.skip:
                continue
            query_vals = catalog.build_from_search_query(query,
                                                         batch_start=batch_start,
                                                         batch_size=batch_size)
            queries[catalog] = query_vals
        # perform search
        for catalog, triplets in queries.items():
            term, fq, params = triplets
            for hit in self._execute_search(catalog, term, fq, params, query):
                yield hit

    def _get_suggestions(self, unused_catalog, events):
        result = set()
        for hits in events.values():
            result.update(x for x, _ in hits)
        return result

    def suggest(self, query, batch_start=None, batch_size=None,
                *unused_args, **unused_kwargs):
        query = ISearchQuery(query)
        clone = self._query_clone(query)
        results = ()
        for catalog in self.query_search_catalogs(query):
            try:
                events = catalog.suggest(clone,
                                         batch_start=batch_start,
                                         batch_size=batch_size)
                if events:  # may be None
                    results = self._get_suggestions(catalog, events)
            except Exception: # pylint: disable=broad-except
                logger.exception("Error while executing query %s on %s",
                                 query, catalog)
        return results
