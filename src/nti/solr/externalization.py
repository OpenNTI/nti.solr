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

from nti.solr.interfaces import IMetadataDocument
from nti.solr.interfaces import ITranscriptDocument

ALL_EXTERNAL_FIELDS = getattr(StandardExternalFields, 'ALL', ())

@interface.implementer(IInternalObjectExternalizer)
class _BasicSOLRExternalizer(InterfaceObjectIO):

	def toExternalObject(self, *args, **kwargs):
		result = super(_BasicSOLRExternalizer, self).toExternalObject(*args, **kwargs)
		for name in ALL_EXTERNAL_FIELDS:
			result.pop(name, None)
		return result

@component.adapter(IMetadataDocument)
@interface.implementer(IInternalObjectExternalizer)
class _MetadataDocumentSOLRExternalizer(_BasicSOLRExternalizer):
	_ext_iface_upper_bound = IMetadataDocument

@component.adapter(ITranscriptDocument)
@interface.implementer(IInternalObjectExternalizer)
class _TranscriptDocumentSOLRExternalizer(_BasicSOLRExternalizer):
	_ext_iface_upper_bound = ITranscriptDocument
