#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.assessment.common import get_containerId

from nti.assessment.interfaces import IQEvaluation
from nti.assessment.interfaces import IQEditableEvaluation

from nti.contentfragments.interfaces import IPlainTextContentFragment

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.publishing.interfaces import IPublishable

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import EVALUATIONS_CATALOG

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IContainersValue
from nti.solr.interfaces import IEvaluationDocument

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import ZERO_DATETIME
from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument
from nti.solr.metadata import DefaultObjectIDValue

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator


class _BasicAttributeValue(object):

    def __init__(self, context=None, default=None):
        self.context = context


@component.adapter(IQEvaluation)
class _DefaultEvaluationIDValue(DefaultObjectIDValue):

    @classmethod
    def createdTime(cls, context):
        if IQEditableEvaluation.providedBy(context):
            return super(_DefaultEvaluationIDValue, cls).createdTime(context)
        return ZERO_DATETIME

    @classmethod
    def creator(cls, context):
        if IQEditableEvaluation.providedBy(context):
            return super(_DefaultEvaluationIDValue, cls).creator(context)
        return SYSTEM_USER_NAME

    def value(self, context=None):
        context = self.context if context is None else context
        if IQEditableEvaluation.providedBy(context):
            if     not IPublishable.providedBy(context) \
                or context.is_published():
                return super(_DefaultEvaluationIDValue, self).creator(context)
            else:
                return None
        return self.prefix(context) + context.ntiid


@component.adapter(IQEvaluation)
@interface.implementer(ITitleValue)
class _DefaultEvaluationTitleValue(_BasicAttributeValue):

    def lang(self, context):
        return 'en'

    def value(self, context=None):
        context = self.context if context is None else context
        return getattr(context, 'title', None)


@component.adapter(IQEvaluation)
@interface.implementer(IContainersValue)
class _DefaultContainerIdValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        result = get_containerId(context)
        return (result,) if result else None


@component.adapter(IQEvaluation)
@interface.implementer(IContentValue)
class _DefaultEvaluationContentValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, context=None):
        return self.language

    def get_content(self, context):
        return getattr(context, 'content', None)

    def value(self, context=None):
        context = self.context if context is None else context
        return self.get_content(context)


@component.adapter(IQEvaluation)
@interface.implementer(IKeywordsValue)
class _DefaultEvaluationKeywordsValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, context=None):
        return self.language

    def value(self, context=None):
        context = self.context if context is None else context
        adapted = IContentValue(context, None)
        if adapted is not None:
            self.language = adapted.lang()
            content = component.getAdapter(adapted.value(),
                                           IPlainTextContentFragment,
                                           name='text')
            return get_keywords(content, self.language)
        return ()


@interface.implementer(IEvaluationDocument)
class EvaluationDocument(MetadataDocument):
    createDirectFieldProperties(IEvaluationDocument)

    mimeType = mime_type = 'application/vnd.nextthought.solr.evaluationdocument'


@component.adapter(IQEvaluation)
@interface.implementer(IEvaluationDocument)
def _EvaluationDocumentCreator(obj, factory=EvaluationDocument):
    return document_creator(obj, factory=factory, provided=IEvaluationDocument)


@component.adapter(IQEvaluation)
@interface.implementer(ICoreCatalog)
def _evaluation_to_catalog(_):
    return component.getUtility(ICoreCatalog, name=EVALUATIONS_CATALOG)


class EvaluationsCatalog(MetadataCatalog):

    skip = False
    name = EVALUATIONS_CATALOG
    document_interface = IEvaluationDocument

    def build_from_search_query(self, query, **kwargs):
        term, fq, params = MetadataCatalog.build_from_search_query(self, query, **kwargs)
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None):
        types = self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        self.client.delete(q=q,
                           commit=self.auto_commit if commit is None else bool(commit))
    reset = clear
