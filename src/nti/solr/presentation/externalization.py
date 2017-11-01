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

from nti.externalization.interfaces import IInternalObjectExternalizer

from nti.solr.presentation.interfaces import IAssetDocument
from nti.solr.presentation.interfaces import ITranscriptDocument

from nti.solr.externalization import CoreDocumentSOLRExternalizer

logger = __import__('logging').getLogger(__name__)


@component.adapter(IAssetDocument)
@interface.implementer(IInternalObjectExternalizer)
class _AssetDocumentSOLRExternalizer(CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = IAssetDocument


@component.adapter(ITranscriptDocument)
@interface.implementer(IInternalObjectExternalizer)
class _TranscriptDocumentSOLRExternalizer(CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = ITranscriptDocument
