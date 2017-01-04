#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
from StringIO import StringIO

from zope import component
from zope import interface

from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.presentation.interfaces import INTITranscript
from nti.contenttypes.presentation.interfaces import IPresentationAsset

from nti.traversal.traversal import find_interface

from nti.solr.interfaces import IContainersValue
from nti.solr.interfaces import ITranscriptSourceValue

from nti.traversal.location import lineage

# assets


@component.adapter(IPresentationAsset)
@interface.implementer(IContainersValue)
class _AssetContainerIdValue(object):

    def __init__(self, context, default=None):
        self.context = context

    @classmethod
    def _container_lineage(cls, context, break_interface):
        result = list()
        for item in lineage(context):
            try:
                ntiid = item.ntiid
                if ntiid:
                    result.append(ntiid)
            except AttributeError:
                pass
            if break_interface.providedBy(item):
                return result, item
        return result, None

    @classmethod
    def _course_containers(cls, context):
        try:
            from nti.contenttypes.courses.interfaces import ICourseInstance
            from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

            containers, item = cls._container_lineage(context, ICourseInstance)
            entry = ICourseCatalogEntry(item, None)
            if entry is not None and entry.ntiid:
                containers.append(entry.ntiid)
            return containers
        except ImportError:
            pass
        return ()

    def value(self, context=None):
        context = self.context if context is None else context
        containers, _ = self._container_lineage(context, IContentPackage)
        if not containers:  # check for courses
            containers = self._course_containers(context)
        return tuple(containers)

# transcripts


@component.adapter(INTITranscript)
@interface.implementer(ITranscriptSourceValue)
class _TranscriptSource(object):

    def __init__(self, context, default=None):
        self.context = context

    def value(self, context=None):
        context = self.context if context is None else context
        src = context.src
        raw_content = None
        # is in content pkg ?
        if 		isinstance(src, six.string_types) \
                and not src.startswith('/')  \
                and '://' not in src:  # e.g. resources/...
            package = find_interface(context, IContentPackage, strict=False)
            if package is not None:
                try:
                    raw_content = package.read_contents_of_sibling_entry(src)
                except Exception:
                    logger.exception("Cannot read contents for %s", src)
        return StringIO(raw_content) if raw_content else None


@component.adapter(INTITranscript)
@interface.implementer(IContainersValue)
class _TranscriptContainerIdValue(_AssetContainerIdValue):

    def value(self, context=None):
        context = self.context if context is None else context
        containers, _ = self._container_lineage(
            context.__parent__, IContentPackage)
        return tuple(containers)
