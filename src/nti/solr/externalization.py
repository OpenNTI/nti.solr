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

from nti.solr.interfaces import IEntityDocument
from nti.solr.interfaces import IMetadataDocument
from nti.solr.interfaces import ITranscriptDocument
from nti.solr.interfaces import IContentUnitDocument

ALL_EXTERNAL_FIELDS = getattr(StandardExternalFields, 'ALL', ())

@interface.implementer(IInternalObjectExternalizer)
class _BasicSOLRExternalizer(InterfaceObjectIO):

	_fields_to_remove = ALL_EXTERNAL_FIELDS

	def toExternalObject(self, *args, **kwargs):
		result = super(_BasicSOLRExternalizer, self).toExternalObject(*args, **kwargs)
		for name in self._fields_to_remove:
			result.pop(name, None)
		return result

@component.adapter(IEntityDocument)
@interface.implementer(IInternalObjectExternalizer)
class _EntityDocumentSOLRExternalizer(_BasicSOLRExternalizer):
	_ext_iface_upper_bound = IEntityDocument

@component.adapter(IContentUnitDocument)
@interface.implementer(IInternalObjectExternalizer)
class _ContentUnitDocumentSOLRExternalizer(_BasicSOLRExternalizer):
	_ext_iface_upper_bound = IContentUnitDocument
	
@component.adapter(IMetadataDocument)
@interface.implementer(IInternalObjectExternalizer)
class _MetadataDocumentSOLRExternalizer(_BasicSOLRExternalizer):
	_ext_iface_upper_bound = IMetadataDocument

@component.adapter(ITranscriptDocument)
@interface.implementer(IInternalObjectExternalizer)
class _TranscriptDocumentSOLRExternalizer(_BasicSOLRExternalizer):
	_ext_iface_upper_bound = ITranscriptDocument
