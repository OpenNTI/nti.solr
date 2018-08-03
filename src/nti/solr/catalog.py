#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from collections import Mapping
from collections import Iterable
from collections import Sequence

import BTrees

import pysolr

import six

from zope import component
from zope import interface

from zope.cachedescriptors.property import Lazy
from zope.cachedescriptors.property import readproperty

from zope.event import notify

from zope.intid.interfaces import IIntIds

from zope.schema.interfaces import IDatetime

from nti.externalization.externalization import to_external_object

from nti.property.property import alias

from nti.schema.eqhash import EqHash

from nti.solr import _OR_
from nti.solr import _AND_
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

from nti.solr.query import QueryTerm
from nti.solr.query import QueryParms
from nti.solr.query import FilterQuery

from nti.solr.query import hl_snippets
from nti.solr.query import search_fields
from nti.solr.query import prepare_solr_query
from nti.solr.query import hl_useFastVectorHighlighter

from nti.solr.schema import SolrDatetime

from nti.solr.utils import normalize_key
from nti.solr.utils import object_finder
from nti.solr.utils import mimeTypeRegistry

from nti.zope_catalog.catalog import ResultSet

logger = __import__('logging').getLogger(__name__)


@EqHash('name')
@interface.implementer(ICoreCatalog)
class CoreCatalog(object):

    __parent__ = None
    __name__ = alias('name')

    skip = False
    max_rows = 500
    auto_commit = True
    return_fields = ('id', 'score')

    name = 'Objects'
    document_interface = ICoreDocument

    family = BTrees.family64

    _OR_ = _OR_
    _AND_ = _AND_

    def __init__(self, core=NTI_CATALOG, name=None, client=None, auto_commit=None):
        self.core = core
        if name is not None:
            self.name = name
        if client is not None:
            self.client = client
        if auto_commit is not None:
            self.auto_commit = bool(auto_commit)

    @readproperty
    def client(self): # pylint: disable=method-hidden
        config = component.getUtility(ISOLR)
        url = config.url + '/%s' % self.core
        return pysolr.Solr(url, timeout=config.timeout)

    # index methods

    def add(self, value, commit=None, event=True):
        adapted = IIDValue(value, None)
        # pylint: disable=too-many-function-args
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
            # pylint: disable=too-many-function-args
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
            # This really shouldn't happen anymore now that we query by site.
            logger.debug('Could not find object with id %r' % doc_id)
        return result

    # zope catalog

    def _fq_from_catalog_query(self, query):
        fq = {}
        for name, value in query.items():
            if name not in self.document_interface:
                continue
            field = self.document_interface[name]
            if isinstance(value, tuple) and len(value) == 2:
                if value[0] == value[1]:
                    value = {'any_of': (value[0],)}
                else:
                    value = {'between': value}
            elif isinstance(value, primitive_types):
                value = {'any_of': (value,)}
            # pylint: disable=unused-variable
            __traceback_info__ = name, value
            assert isinstance(value, Mapping) and len(value) == 1, \
                   'Invalid field query'
            for k, v in value.items():
                if k == 'any_of':
                    values = (lucene_escape(x) for x in v)
                    fq[name] = "(%s)" % self._OR_.join(values)
                elif k == 'all_of':
                    values = (lucene_escape(x) for x in v)
                    fq[name] = "(%s)" % self._AND_.join(values)
                elif k == 'between':
                    if IDatetime.providedBy(field):
                        v = [SolrDatetime.toUnicode(x) for x in v]
                    data = (lucene_escape(v[0]), lucene_escape(v[1]))
                    fq[name] = "[%s TO %s]" % data
        return fq

    def _build_from_catalog_query(self, query):
        fq = self._fq_from_catalog_query(query)
        return ('*:*', fq, {'fl': ','.join(self.return_fields)})

    def apply(self, query):
        if isinstance(query, primitive_types):
            if not isinstance(query, six.string_types):
                query = str(query)
            term, fq, params = query, {}, {'fl': ','.join(self.return_fields)}
        else:
            term, fq, params = self._build_from_catalog_query(query)
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
                adapted = IIntIdValue(obj, None)  # get intid
                # pylint: disable=too-many-function-args
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
        # pylint: disable=no-value-for-parameter
        for name, field in self.document_interface.namesAndDescriptions(all=True):
            if ITextField.providedBy(field):
                result.append(name)
        return result
    search_fields = text_fields  # text fields are used for search

    def _fq_from_search_query(self, query):
        fq = FilterQuery()
        for name, value in query.items():
            if name not in self.document_interface:
                continue
            field = self.document_interface[name]
            if isinstance(value, six.string_types):
                fq.add_term(name, lucene_escape(value))
            elif isinstance(value, Sequence) and len(value) == 2:  # range
                if IDatetime.providedBy(field):
                    value = [SolrDatetime.toUnicode(x) for x in value]
                data = (lucene_escape(value[0]), lucene_escape(value[1]))
                fq.add_term(name, "[%s TO %s]" % data)
            elif isinstance(value, Iterable) and value:  # OR list
                data = (lucene_escape(x) for x in value)
                fq.add_term(name, "(%s)" % self._OR_.join(data))
            elif value is not None:
                fq.add_term(name, lucene_escape(str(value)))
        return fq

    def _params_from_search_query(self, query):
        params = QueryParms()
        if self.text_fields and getattr(query, 'applyHighlights', None):
            params['hl'] = 'true'
            params['hl.fl'] = self.text_fields
            params['hl.requireFieldMatch'] = 'true'
            params['hl.simple.pre'] = params['hl.tag.pre'] = '<hit>'
            params['hl.simple.post'] = params['hl.tag.post'] = '</hit>'
            if hl_useFastVectorHighlighter(query):
                params['hl.useFastVectorHighlighter'] = 'true'
            params['hl.snippets'] = hl_snippets(query)
        # return fields
        params['fl'] = self.return_fields
        return params

    def _build_term_from_search_query(self, query):
        qt = QueryTerm()
        term = getattr(query, 'term', query)
        if term: # want to make sure we have something to search
            fields = search_fields(query, self.search_fields)
            # pylint: disable=using-constant-test, not-an-iterable
            if fields:
                for name in fields:
                    qt.add_term(name, term)
            else:
                qt.default = term
        return qt

    def build_from_search_query(self, query, batch_start=None, batch_size=None):
        term = self._build_term_from_search_query(query)
        # filter query
        fq = self._fq_from_search_query(query)
        # parameters
        params = self._params_from_search_query(query)
        # batching
        if batch_start is not None and batch_size:
            params['start'] = str(batch_start)
            params['rows'] = str(batch_size)
        else:
            params['rows'] = str(self.max_rows)  # default number of rows
        # query-term, filter-query, params
        return (term, fq, params)

    def _prepare_solr_query(self, term, fq, params):
        return prepare_solr_query(term, fq, params)

    def filter(self, unused_event, unused_query=None):
        return False

    def execute(self, term, fq, params, unused_query=None):
        term, params = self._prepare_solr_query(term, fq, params)
        return self.client.search(term, **params)

    def search(self, query, *args, **kwargs):
        term, fq, params = self.build_from_search_query(query, *args, **kwargs)
        return self.execute(term, fq, params, query)

    # content search / ISearcher.suggest

    def get_mime_types(self, catalog=None):
        catalog = catalog or self.name
        return mimeTypeRegistry.getMimeTypes(catalog)

    @Lazy
    def suggest_fields(self):
        result = []
        # pylint: disable=no-value-for-parameter
        for name, field in self.document_interface.namesAndDescriptions(all=True):
            if ISuggestField.providedBy(field):
                result.append(name)
        return result

    def _prepare_solr_suggest(self, query, batch_start=None, batch_size=None):
        params = {}
        limit = getattr(query, 'limit', None)
        if limit:
            params['terms.limit'] = limit
        if batch_start is not None and batch_size:
            params['start'] = str(batch_start)
            params['rows'] = str(batch_size)
        return params

    # pylint: disable=keyword-arg-before-vararg
    def suggest(self, query, fields=None, batch_start=None, batch_size=None, 
                *unused_args, **unused_kwargs):
        suggest_fields = fields or self.suggest_fields
        params = self._prepare_solr_suggest(query,
                                            batch_start=batch_start,
                                            batch_size=batch_size)
        if suggest_fields:
            return self.client.suggest_terms(suggest_fields, query.term, **params)

    def delete(self, uid=None, q=None, commit=True):
        return self.client.delete(id=uid, q=q, commit=commit)
