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

from nti.solr.courses.interfaces import ICourseCatalogDocument

from nti.solr.externalization import CoreDocumentSOLRExternalizer

logger = __import__('logging').getLogger(__name__)


@component.adapter(ICourseCatalogDocument)
@interface.implementer(IInternalObjectExternalizer)
class _CourseCatalogDocumentSOLRExternalizer(CoreDocumentSOLRExternalizer):
    _ext_iface_upper_bound = ICourseCatalogDocument
