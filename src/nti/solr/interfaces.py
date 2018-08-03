#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.index.interfaces import IInjection
from zope.index.interfaces import IIndexSearch

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.location.interfaces import IContained

from nti.base.interfaces import IDict

from nti.contentsearch.interfaces import ISearcher
from nti.contentsearch.interfaces import ISearchQueryValidator

from nti.solr.schema import SolrDatetime

from nti.schema.field import Bool
from nti.schema.field import IndexedIterable
from nti.schema.field import DecodingValidTextLine as ValidTextLine


class ITextField(interface.Interface):
    """
    Marker interface for text fields
    """


class ISuggestField(interface.Interface):
    """
    Marker interface for suggest fields
    """


class IDateField(interface.Interface):
    """
    Marker interface for date fields
    """


class IAttributeValue(interface.Interface):
    """
    Adapter interface to get the [field] value from a given object
    """

    def value():
        """
        Return the attribute value for a given adapted object
        """


class IIDValue(IAttributeValue):
    """
    Adapter interface to get the id value from a given object
    """


class IStringValue(IAttributeValue):
    """
    Marker interface to get a 'string' value from a given object
    """

    def lang():
        """
        Return the lang code for a 'string' value from a given object
        """

# metadata


class IIntIdValue(IAttributeValue):
    """
    Adapter interface to get the int id value from a given object
    """


class ISiteValue(IAttributeValue):
    """
    Adapter interface to get the site value from a given object
    """


class ICreatorValue(IAttributeValue):
    """
    Adapter interface to get the creator value from a given object
    """


class IMimeTypeValue(IAttributeValue):
    """
    Adapter interface to get the mimeType value from a given object
    """


class ITaggedToValue(IAttributeValue):
    """
    Adapter interface to get the tagged-to value from a given object
    """


class IInReplyToValue(IAttributeValue):
    """
    Adapter interface to get the in-reply-to value from a given object
    """


class IContainersValue(IAttributeValue):
    """
    Adapter interface to get the containerId values from a given object
    """
IContainerIdValue = IContainersValue


class ISharedWithValue(IAttributeValue):
    """
    Adapter interface to get the sharedWith value from a given object
    """


class ICreatedTimeValue(IAttributeValue):
    """
    Adapter interface to get the createdTime value from a given object
    """


class ILastModifiedValue(IAttributeValue):
    """
    Adapter interface to get the lastModified value from a given object
    """


class IIsDeletedObjectValue(IAttributeValue):
    """
    Adapter interface to check if the object is deleted
    """


class IIsUserGeneratedDataValue(IAttributeValue):
    """
    Adapter interface to check if the object is UGD
    """


class IIsTopLevelContentValue(IAttributeValue):
    """
    Adapter interface to get the isTopLevelContent value from a given object
    """


class IContainerContextValue(IAttributeValue):
    """
    Adapter interface to get the container context value from a given object
    """


def tagField(field, stored=True, adapter=None, multiValued=False, indexed=True,
             type_=None, boost=None, provided=None):
    field.setTaggedValue('__solr_stored__', stored)
    field.setTaggedValue('__solr_indexed__', indexed)
    field.setTaggedValue('__solr_multiValued__', multiValued)
    field.setTaggedValue('__solr_value_interface__', adapter)
    if type_ is not None:
        field.setTaggedValue('__solr_type__', type_)
    if boost is not None:
        field.setTaggedValue('__solr_boost__', boost)
    if provided is not None:
        if not isinstance(provided, (list, tuple, set)):
            provided = (provided,)
        for iface in provided:
            interface.alsoProvides(field, iface)


class ICoreDocument(interface.Interface):
    id = ValidTextLine(title=u'The id', required=True)

tagField(ICoreDocument['id'], True, IIDValue)


class IMetadataDocument(ICoreDocument):

    site = ValidTextLine(title=u'The site', required=False)

    creator = ValidTextLine(title=u'The creator', required=False)

    mimeType = ValidTextLine(title=u'The mime type', required=False)

    taggedTo = IndexedIterable(title=u'The entities identifiers',
                               required=False,
                               value_type=ValidTextLine(title=u"The entiy identifier"),
                               min_length=0)

    inReplyTo = ValidTextLine(title=u'The replied to NTIID', required=False)

    containerId = IndexedIterable(title=u'The container identifiers',
                                  required=False,
                                  value_type=ValidTextLine(title=u"The container identifier"),
                                  min_length=0)

    sharedWith = IndexedIterable(title=u'The entities shared with',
                                 required=False,
                                 value_type=ValidTextLine(title=u"The entiy"),
                                 min_length=0)

    containerContext = ValidTextLine(title=u'The container context',
                                     required=False)

    createdTime = SolrDatetime(title=u'The created date', required=False)

    lastModified = SolrDatetime(title=u'The last modified date', \
                                required=False)

    isDeletedObject = Bool(title=u'Is deleted object flag', required=False)

    isTopLevelContent = Bool(title=u'Is top level object flag', required=False)

    isUserGeneratedData = Bool(title=u'Is UGD object flag', required=False)


tagField(IMetadataDocument['site'], False, ISiteValue)

tagField(IMetadataDocument['creator'], True, ICreatorValue)

tagField(IMetadataDocument['mimeType'], True, IMimeTypeValue)

tagField(IMetadataDocument['inReplyTo'], False, IInReplyToValue)

tagField(IMetadataDocument['isDeletedObject'], False, IIsDeletedObjectValue)

tagField(IMetadataDocument['containerContext'], False, IContainerContextValue)

tagField(IMetadataDocument['isTopLevelContent'],
         False, IIsTopLevelContentValue)

tagField(IMetadataDocument['isUserGeneratedData'],
         False, IIsUserGeneratedDataValue)

tagField(IMetadataDocument['taggedTo'], True, ITaggedToValue,
         multiValued=True)

tagField(IMetadataDocument['sharedWith'], True,
         ISharedWithValue, multiValued=True)

tagField(IMetadataDocument['containerId'], False,
         IContainersValue, multiValued=True)

tagField(IMetadataDocument['createdTime'], False,
         ICreatedTimeValue, provided=IDateField)

tagField(IMetadataDocument['lastModified'], False,
         ILastModifiedValue, provided=IDateField)


# misc


class IContentValue(IStringValue):
    """
    Adapter interface to get the content value from a given object
    """


class IKeywordsValue(IStringValue):
    """
    Adapter interface to get the keywords value from a given object
    """

    def lang():
        """
        Return the lang code for a keywords value from a given object
        """


class INTIIDValue(IAttributeValue):
    """
    Adapter interface to get the ntiid value from a given object
    """


class ITitleValue(IStringValue):
    """
    Adapter interface to get the title value from a given object
    """


class ITagsValue(IAttributeValue):
    """
    Adapter interface to get the tag values from a given object
    """


class ICoreCatalog(IInjection, IIndexSearch, IContained):

    name = ValidTextLine(title=u"Catalog name", required=True)
    core = ValidTextLine(title=u"Core/Collection name", required=True)

    text_fields = IndexedIterable(title=u'The text fields',
                                  required=False,
                                  value_type=ValidTextLine(title=u"The field name"),
                                  min_length=0,
                                  readonly=True)

    search_fields = IndexedIterable(title=u'The search fields',
                                    required=False,
                                    value_type=ValidTextLine(title=u"The field name"),
                                    min_length=0,
                                    readonly=True)
    
    suggest_fields = IndexedIterable(title=u'The text fields',
                                     required=False,
                                     value_type=ValidTextLine(title=u"The field name"),
                                     min_length=0,
                                     readonly=True)

    return_fields = IndexedIterable(title=u'The fields to return',
                                    required=False,
                                    value_type=ValidTextLine(title=u"The field name"),
                                    min_length=0,
                                    readonly=True)

    def add(value, commit=True, event=True):
        """
        Add a document to the index.

        :param value: the object to be indexed
        :param commit: Commit operation
        :param event: Notification event
        """

    def remove(value, commit=True, event=True):
        """
        Remove a document from the index

        :param value: The object/id to remove
        :param commit: Commit operation
        :param event: Notification event
        """

    def delete(uid=None, q=None, commit=True):
        """
        Delete by the specified query or id

        :param uid: The object/id to remove
        :param q: The query to execute for deletion
        :param commit: Commit operation
        """

    def build_from_search_query(query, batch_start=None, batch_size=None):
        """
        Return a triplet
        (:class:`ISOLRQueryTerm`,
         :class:`ISOLRFilterQuery`,
         :class:`ISOLRQueryParams`) from the specified query

        :param query a :class:`nti.contentsearch.interfaces.ISearcherQuery` object
        :param batch_start the starting item to fetch from the searcher
        :param batch_size the number of items needed from the searcher
        """

    def filter(self, event, query=None):
        """
        Return True if the event needs to be filtered

        :param event solr event dict return 
        :param param query a :class:`nti.contentsearch.interfaces.ISearcherQuery` object
        """

    def execute(term, fq, params, query=None):
        """
        Execute a solr search

        :param term a :class:`ISOLRQueryTerm` object
        :param fq a :class:`ISOLRFilterQuery` object
        :param params a :class:`ISOLRQueryParams` object
        """


class IEvaluationCatalog(ICoreCatalog):
    """
    Defines an Evaluations catalog
    """

class ILibraryCatalog(ICoreCatalog):
    """
    Defines a content library catalog
    """

class ICourseCatalog(ICoreCatalog):
    """
    Defines a course library catalog
    """

class IEntityCatalog(ICoreCatalog):
    """
    Defines an entity catalog
    """

class IPresentationAssetCatalog(ICoreCatalog):
    """
    Defines a presentation asset catalog
    """

class ITranscriptCatalog(ICoreCatalog):
    """
    Defines a transcript catalog
    """

class IUserDataCatalog(ICoreCatalog):
    """
    Defines a user-data catalog
    """

class IIndexObjectEvent(IObjectEvent):
    """
    Event to signal object must be indexed
    """


@interface.implementer(IIndexObjectEvent)
class IndexObjectEvent(ObjectEvent):
    pass


class IUnindexObjectEvent(IObjectEvent):
    """
    Event to signal object must be unindexed
    """


@interface.implementer(IUnindexObjectEvent)
class UnindexObjectEvent(ObjectEvent):
    pass


class IObjectIndexedEvent(IObjectEvent):
    """
    Event to signal an object has been indexed
    """
    doc_id = ValidTextLine(title=u'Document id')


@interface.implementer(IObjectIndexedEvent)
class ObjectIndexedEvent(ObjectEvent):

    def __init__(self, obj, doc_id=None):
        ObjectEvent.__init__(self, obj)
        self.doc_id = doc_id


class IObjectUnindexedEvent(IObjectEvent):
    """
    Event to signal an object has been unindexed
    """
    doc_id = ValidTextLine(title=u'Document id')


@interface.implementer(IObjectUnindexedEvent)
class ObjectUnindexedEvent(ObjectEvent):

    def __init__(self, obj, doc_id=None):
        ObjectEvent.__init__(self, obj)
        self.doc_id = doc_id


# registration

class ISOLRQueueFactory(interface.Interface):
    """
    A factory for SOLR processing queues.
    """


class ISOLR(interface.Interface):
    URL = ValidTextLine(title=u"LDAP URL", required=True)
    Timeout = ValidTextLine(title=u"Timeout", required=False)

# searcher


class ISOLRSearcher(ISearcher):

    def suggest(query, fields=None, batch_start=None, batch_size=None, *args, **kwargs):
        pass


class ISOLRQueryValidator(ISearchQueryValidator):
    pass


class ISOLRFilterQuery(interface.Interface):

    def add_term(name, value):
        """
        add a single field search term

        :param name: Field name
        :param value: Field value
        """

    def add_or(name, values):
        """
        add an OR field search values

        :param name: Field name
        :param value: Field values
        """

    def add_and(name, values):
        """
        add an AND field search values

        :param name: Field name
        :param value: Field values
        """

    def to_solr():
        """"
        return a string with SOLR filter query term
        """

    def __contains__(*args, **kwargs):
        pass

    def __iadd__(other):
        pass


class ISOLRQueryTerm(interface.Interface):

    default = ValidTextLine(title=u"Default search term",
                            required=False,
                            default=None)

    def add_term(name, value):
        """
        add a single field search term

        :param name: Field name
        :param value: Field value
        """

    def to_solr():
        """"
        return a string with SOLR query term
        """

    def __contains__(*args, **kwargs):
        pass

    def __iadd__(other):
        pass


class ISOLRQueryParams(IDict):

    def to_solr():
        """"
        return a map with SOLR query params
        """

    def __iadd__(other):
        pass
