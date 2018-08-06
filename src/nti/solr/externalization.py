#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.externalization.datastructures import InterfaceObjectIO

from nti.externalization.interfaces import IInternalObjectExternalizer

from nti.externalization.interfaces import StandardExternalFields

from nti.solr.interfaces import ICoreDocument
from nti.solr.interfaces import IMetadataDocument

ALL_EXTERNAL_FIELDS = getattr(StandardExternalFields, 'ALL', ())

logger = __import__('logging').getLogger(__name__)


@component.adapter(ICoreDocument)
@interface.implementer(IInternalObjectExternalizer)
class CoreDocumentSOLRExternalizer(InterfaceObjectIO):

    _ext_iface_upper_bound = ICoreDocument

    _fields_to_remove = set(ALL_EXTERNAL_FIELDS) - {'mimeType'}

    def toExternalObject(self, *args, **kwargs):  # pylint: disable=arguments-differ
        kwargs['decorate'] = False
        result = super(CoreDocumentSOLRExternalizer, self).toExternalObject(*args, **kwargs)
        for name in self._fields_to_remove:
            result.pop(name, None)
        for name, value in list(result.items()):
            if value in ([], (), None):
                result.pop(name, None)
        return result
_CoreDocumentSOLRExternalizer = CoreDocumentSOLRExternalizer


@component.adapter(IMetadataDocument)
@interface.implementer(IInternalObjectExternalizer)
class _MetadataDocumentSOLRExternalizer(CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IMetadataDocument
