#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.externalization.datastructures import InterfaceObjectIO

from nti.externalization.interfaces import IInternalObjectExternalizer

from nti.externalization.interfaces import StandardExternalFields

from nti.solr.interfaces import ICoreDocument
from nti.solr.interfaces import IAssetDocument
from nti.solr.interfaces import IEntityDocument
from nti.solr.interfaces import IMetadataDocument
from nti.solr.interfaces import IUserDataDocument
from nti.solr.interfaces import IEvaluationDocument
from nti.solr.interfaces import ITranscriptDocument
from nti.solr.interfaces import IContentUnitDocument
from nti.solr.interfaces import ICourseCatalogDocument

ALL_EXTERNAL_FIELDS = getattr(StandardExternalFields, 'ALL', ())


@component.adapter(ICoreDocument)
@interface.implementer(IInternalObjectExternalizer)
class _CoreDocumentSOLRExternalizer(InterfaceObjectIO):

    _ext_iface_upper_bound = ICoreDocument

    _fields_to_remove = set(
        ALL_EXTERNAL_FIELDS) - {StandardExternalFields.CTA_MIMETYPE}

    def toExternalObject(self, *args, **kwargs):
        kwargs['decorate'] = False
        result = super(_CoreDocumentSOLRExternalizer, self).toExternalObject(
            *args, **kwargs)
        for name in self._fields_to_remove:
            result.pop(name, None)
        for name, value in list(result.items()):
            if value in ([], (), None):
                result.pop(name, None)
        return result


@component.adapter(IEntityDocument)
@interface.implementer(IInternalObjectExternalizer)
class _EntityDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IEntityDocument


@component.adapter(IContentUnitDocument)
@interface.implementer(IInternalObjectExternalizer)
class _ContentUnitDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IContentUnitDocument


@component.adapter(IMetadataDocument)
@interface.implementer(IInternalObjectExternalizer)
class _MetadataDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IMetadataDocument


@component.adapter(ITranscriptDocument)
@interface.implementer(IInternalObjectExternalizer)
class _TranscriptDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = ITranscriptDocument


@component.adapter(IUserDataDocument)
@interface.implementer(IInternalObjectExternalizer)
class _UserDataDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IUserDataDocument


@component.adapter(IAssetDocument)
@interface.implementer(IInternalObjectExternalizer)
class _AssetDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IAssetDocument


@component.adapter(ICourseCatalogDocument)
@interface.implementer(IInternalObjectExternalizer)
class _CourseCatalogDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = ICourseCatalogDocument


@component.adapter(IEvaluationDocument)
@interface.implementer(IInternalObjectExternalizer)
class _EvaluationDocumentSOLRExternalizer(_CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IEvaluationDocument
