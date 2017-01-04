#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import copy
from collections import defaultdict

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIds

from nti.contentsearch.interfaces import ISearchHit
from nti.contentsearch.interfaces import ISearchQuery

from nti.contentsearch.search_fragments import SearchFragment

from nti.contentsearch.search_results import SearchResults
from nti.contentsearch.search_results import SuggestResults

from nti.dataserver.interfaces import IUser

from nti.property.property import Lazy

from nti.solr import USERDATA_CATALOG

from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ISOLRSearcher

from nti.solr.query import prepare_solr_triplets

from nti.solr.utils import normalize_field
from nti.solr.utils import mimeTypeRegistry


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
        if query.searchOn:
            catalogs = set()
            for mimeType in query.searchOn:
                # look for a mimeType catalog utility
                catalog = component.queryUtility(ICoreCatalog, name=mimeType)
                if catalog is None:  # use mapper
                    name = mimeTypeRegistry.getCatalog(mimeType, u'')
                    catalog = component.queryUtility(ICoreCatalog, name=name)
                if catalog is None:  # defaults to userdata
                    catalog = component.queryUtility(
                        ICoreCatalog, name=USERDATA_CATALOG)
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
        except Exception as e:
            logger.debug('Could not create hit for %s. %s', result, e)
        return None

    def _do_search(self, catalog, term, params):
        try:
            events = catalog.client.search(term, **params)
            for event in events or ():
                hit = self._get_search_hit(catalog, event, events.highlighting)
                if hit is not None:
                    yield hit
        except Exception:
            logger.exception("Error while executing query %s", term)

    def search(self, query, *args, **kwargs):
        cores = {}
        queries = defaultdict(list)
        query = ISearchQuery(query)
        catalogs = self.query_search_catalogs(query)
        result = SearchResults(Name="Hits", Query=query)
        # collect catalogs by core and build query triplets
        for catalog in catalogs or ():
            if catalog.skip:
                continue
            core = catalog.core
            cores[core] = catalog  # store
            queries[core].append(catalog.build_from_search_query(query))
        # perform search
        for core, triplet in queries.items():
            catalog = cores[core]
            term, params = prepare_solr_triplets(triplet)
            for hit in self._do_search(catalog, term, params):
                result.add(hit)
        return result

    def _get_suggestions(self, catalog, events):
        result = set()
        for hits in events.values():
            result.update(x for x, _ in hits)
        return result

    def suggest(self, query, *args, **kwargs):
        query = ISearchQuery(query)
        clone = self._query_clone(query)
        result = SuggestResults(Name="Suggestions", Query=query)
        for catalog in self.query_search_catalogs(query):
            try:
                events = catalog.suggest(clone)
                if events:  # may be None
                    result.extend(self._get_suggestions(catalog, events))
            except Exception:
                logger.exception(
                    "Error while executing query %s on %s", query, catalog)
        return result
