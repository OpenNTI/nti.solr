#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import six
import functools
from itertools import chain
from collections import defaultdict

import gevent

from zope import component

from zope.component.hooks import getSite

from zope.interface.interfaces import IMethod

from zope.intid.interfaces import IIntIds

from nti.base._compat import text_

from nti.contentprocessing.content_utils import tokenize_content

from nti.contentprocessing.interfaces import IStopWords

from nti.contentprocessing.keyword import extract_key_words

from nti.contenttypes.presentation import AUDIO_MIME_TYPES
from nti.contenttypes.presentation import VIDEO_MIME_TYPES
from nti.contenttypes.presentation import TIMELINE_MIME_TYPES
from nti.contenttypes.presentation import RELATED_WORK_REF_MIME_TYPES

from nti.ntiids.ntiids import is_valid_ntiid_string
from nti.ntiids.ntiids import find_object_with_ntiid

from nti.schema.interfaces import find_most_derived_interface

from nti.solr import ASSETS_CATALOG
from nti.solr import COURSES_CATALOG
from nti.solr import ENTITIES_CATALOG
from nti.solr import USERDATA_CATALOG
from nti.solr import EVALUATIONS_CATALOG
from nti.solr import TRANSCRIPTS_CATALOG
from nti.solr import CONTENT_UNITS_CATALOG

from nti.solr.interfaces import IStringValue
from nti.solr.interfaces import ICoreDocument

from nti.solr.termextract import extract_key_words as term_extract_key_words

logger = __import__('logging').getLogger(__name__)


# content


def resolve_content_parts(data):
    result = []
    data = [data] if isinstance(data, six.string_types) else data
    for item in data or ():
        adapted = IStringValue(item, None)
        if adapted is not None:
            result.append(adapted.value())
    result = u'\n'.join(x for x in result if x is not None)
    return result


def get_content(text=None, lang="en"):
    if not text or not isinstance(text, six.string_types):
        result = u''
    else:
        text = text_(text)
        result = tokenize_content(text, lang)
        result = u' '.join(result) if result else text
    return result


def get_keywords(content, lang='en'):
    stopwords = ()
    utility = component.queryUtility(IStopWords)
    if utility is not None:
        stopwords = utility.stopwords(lang) or ()
    keywords = extract_key_words(content, lang=lang)
    if not keywords:
        keywords = term_extract_key_words(content,
                                          lang=lang,
                                          blacklist=stopwords)
    return keywords


# documents


def document_creator(obj, factory, provided=None):
    result = factory()
    if provided is None:
        provided = find_most_derived_interface(result, ICoreDocument)
    for k, v in provided.namesAndDescriptions(all=True):
        __traceback_info__ = k, v
        if IMethod.providedBy(v):
            continue
        value_interface = v.queryTaggedValue('__solr_value_interface__')
        if value_interface is None:
            continue
        adapted = value_interface(obj, None)
        if adapted is not None:
            value = adapted.value()
            setattr(result, k, value)
    return result

# pattern to get any prefix and/or post fix that a catalog may add to the
# document ids. The prefix is anything that comes before the first '#' and
# may be use as split.key for sharding. The postfix is anything after '='
# in this application ids CANNOT have an '='
_key_pattern = re.compile(r'([a-zA-Z0-9_.+-:,@]+\#)?([a-zA-Z0-9_.+-:,@\(\)]+)(=.*)?$',
                          re.UNICODE | re.IGNORECASE)


def normalize_key(doc_id):
    m = _key_pattern.match(doc_id)
    if m is not None:
        return m.groups()[1]
    return doc_id


def object_finder(doc_id, intids=None):
    doc_id = normalize_key(doc_id)
    if is_valid_ntiid_string(doc_id):
        return find_object_with_ntiid(doc_id)
    else:
        intids = component.getUtility(IIntIds) if intids is None else intids
        try:
            return intids.queryObject(int(doc_id))
        except (ValueError, TypeError):
            logger.error("Cannot get object with id %s", doc_id)


_f_pattern = re.compile(r'(.*)(_[a-z]{2})$', re.UNICODE | re.IGNORECASE)


def normalize_field(name):
    m = _f_pattern.match(name)
    if m is not None:
        return m.groups()[0]
    return name


# searcher


def transacted_func(func=None, **kwargs):
    assert func is not None

    # prepare function call
    new_callable = functools.partial(func, **kwargs)

    site_names = (getSite().__name__,)

    def _runner():
        from nti.site.interfaces import ISiteTransactionRunner
        transaction_runner = component.getUtility(ISiteTransactionRunner)
        transaction_runner = functools.partial(transaction_runner,
                                               site_names=site_names,
                                               side_effect_free=True)
        return transaction_runner(new_callable)

    return _runner


def gevent_spawn(func=None, **kwargs):
    greenlet = gevent.spawn(transacted_func(func, **kwargs))
    return greenlet


# MimeType / Catalog registry


class MimeTypeRegistry(object):

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(MimeTypeRegistry, cls).__new__(
                cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        self.mime_type_catalog = {}
        self.catalog_mime_type = defaultdict(set)

    def register_mime_type(self, mimeType, catalog):
        if mimeType in self.mime_type_catalog:
            raise ValueError("mimeType already registered")
        if catalog == USERDATA_CATALOG:
            raise ValueError("Cannot register in userdata catalog")
        self.mime_type_catalog[mimeType] = catalog
        self.catalog_mime_type[catalog].add(mimeType)
        self.catalog_mime_type[USERDATA_CATALOG].add(mimeType)  # Negative list
    register = register_mime_type

    def get_catalog(self, mimeType, default=None):
        return self.mime_type_catalog.get(mimeType, default)
    getCatalog = get_catalog

    def get_mime_types(self, catalog, default=()):
        result = self.catalog_mime_type.get(catalog)
        return tuple(result) if result else default
    getMimeTypes = get_mime_types

# Global registry
mimeTypeRegistry = MimeTypeRegistry()

# Known mimeTypes used to map to their corresponding  search catalogs
CONTENT_MIME_TYPE = 'application/vnd.nextthought.content'
BOOK_CONTENT_MIME_TYPE = 'application/vnd.nextthought.bookcontent'

NTI_TRANSCRIPT_MIME_TYPE = 'application/vnd.nextthought.ntitranscript'
AUDIO_TRANSCRIPT_MIME_TYPE = 'application/vnd.nextthought.audiotranscript'
VIDEO_TRANSCRIPT_MIME_TYPE = 'application/vnd.nextthought.videotranscript'

COURSE_MIME_TYPE = 'application/vnd.nextthought.courses.courseinstance'
CATALOG_ENTRY_MIME_TYPE = 'application/vnd.nextthought.courses.coursecatalogentry'
CATALOG_LEGACY_ENTRY_MIME_TYPE = 'application/vnd.nextthought.courses.coursecataloglegacyentry'

USER_MIME_TYPE = 'application/vnd.nextthought.user'
COMMUNITY_MIME_TYPE = 'application/vnd.nextthought.community'
DFL_MIME_TYPE = 'application/vnd.nextthought.dynamicfriendslist'
FRIEND_LISTS_MIME_TYPE = 'application/vnd.nextthought.friendslist'


def _register():
    # transcripts
    mimeTypeRegistry.register(NTI_TRANSCRIPT_MIME_TYPE, TRANSCRIPTS_CATALOG)
    mimeTypeRegistry.register(AUDIO_TRANSCRIPT_MIME_TYPE, TRANSCRIPTS_CATALOG)
    mimeTypeRegistry.register(VIDEO_TRANSCRIPT_MIME_TYPE, TRANSCRIPTS_CATALOG)

    # courses
    mimeTypeRegistry.register(COURSE_MIME_TYPE, COURSES_CATALOG)
    mimeTypeRegistry.register(CATALOG_ENTRY_MIME_TYPE, COURSES_CATALOG)
    mimeTypeRegistry.register(CATALOG_LEGACY_ENTRY_MIME_TYPE, COURSES_CATALOG)

    # entities
    mimeTypeRegistry.register(DFL_MIME_TYPE, ENTITIES_CATALOG)
    mimeTypeRegistry.register(USER_MIME_TYPE, ENTITIES_CATALOG)
    mimeTypeRegistry.register(COMMUNITY_MIME_TYPE, ENTITIES_CATALOG)
    mimeTypeRegistry.register(FRIEND_LISTS_MIME_TYPE, ENTITIES_CATALOG)

    # assets
    for m in chain(AUDIO_MIME_TYPES,
                   VIDEO_MIME_TYPES,
                   TIMELINE_MIME_TYPES,
                   RELATED_WORK_REF_MIME_TYPES):
        mimeTypeRegistry.register(m, ASSETS_CATALOG)

    # evaluations
    try:
        from nti.assessment.interfaces import ALL_EVALUATION_MIME_TYPES
        for m in ALL_EVALUATION_MIME_TYPES:
            mimeTypeRegistry.register(m, EVALUATIONS_CATALOG)
    except ImportError:
        pass

    # content
    try:
        from nti.contentlibrary import ALL_CONTENT_MIMETYPES
        for m in ALL_CONTENT_MIMETYPES:
            mimeTypeRegistry.register(m, CONTENT_UNITS_CATALOG)
        mimeTypeRegistry.register(CONTENT_MIME_TYPE, CONTENT_UNITS_CATALOG)
        mimeTypeRegistry.register(BOOK_CONTENT_MIME_TYPE, CONTENT_UNITS_CATALOG)
    except ImportError:
        pass

_register()
del _register
