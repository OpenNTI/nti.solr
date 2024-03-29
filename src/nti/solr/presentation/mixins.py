#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from six import StringIO
from six import string_types

from zope import component
from zope import interface

from nti.base.interfaces import IFile

from nti.contenttypes.presentation.interfaces import INTITranscript
from nti.contenttypes.presentation.interfaces import IPresentationAsset

from nti.traversal.traversal import find_interface

from nti.solr.interfaces import IContainersValue

from nti.solr.presentation.interfaces import ITranscriptSourceValue

from nti.traversal.location import lineage

try:
    from nti.contentlibrary.interfaces import IContentPackage
    HAS_CONTENT_LIBRARY = True
except ImportError:
    HAS_CONTENT_LIBRARY = False
    IContentPackage = interface.Interface
    
try:
    from nti.contenttypes.courses.interfaces import ICourseInstance
    from nti.contenttypes.courses.interfaces import ICourseCatalogEntry
    HAS_COURSE = True
except ImportError:
    HAS_COURSE = False
    ICourseInstance = ICourseCatalogEntry = interface.Interface
    

logger = __import__('logging').getLogger(__name__)


# assets


@component.adapter(IPresentationAsset)
@interface.implementer(IContainersValue)
class _AssetContainerIdValue(object):

    def __init__(self, context, unused_default=None):
        self.context = context

    @classmethod
    def _get_ntiid(cls, context):
        try:
            return context.ntiid
        except AttributeError:
            return None

    @classmethod
    def _container_lineage(cls, context, break_interface=None):
        result = None
        ntiids = list()
        for item in lineage(context):
            if item is context:
                continue
            ntiid = cls._get_ntiid(item)
            if ntiid:
                ntiids.append(ntiid)
            if break_interface is not None and break_interface.providedBy(item):
                result = item
                break
        return ntiids, result

    @classmethod
    def _package_containers(cls, context):
        if HAS_CONTENT_LIBRARY:
            containers, _ = cls._container_lineage(context, IContentPackage)
            return containers
        return ()

    @classmethod
    def _course_containers(cls, context):
        if HAS_COURSE:
            containers, item = cls._container_lineage(context, ICourseInstance)
            entry = ICourseCatalogEntry(item, None)
            if entry is not None and entry.ntiid:
                containers.append(entry.ntiid)
            return containers
        return ()

    def value(self, context=None):
        context = self.context if context is None else context
        containers = self._package_containers(context)
        if not containers:  # check for courses
            containers = self._course_containers(context)
        return tuple(containers)


# transcripts


@component.adapter(INTITranscript)
@interface.implementer(ITranscriptSourceValue)
class _TranscriptSource(object):

    def __init__(self, context, unused_default=None):
        self.context = context

    def library_source(self, context, source):
        if HAS_CONTENT_LIBRARY:
            raw_content = None
            # is in content pkg ?
            if      not source.startswith('/')  \
                and '://' not in source:  # e.g. resources/...
                package = find_interface(context, IContentPackage, strict=False)
                if package is not None:
                    try:
                        raw_content = package.read_contents_of_sibling_entry(source)
                    except Exception:
                        logger.exception("Cannot read contents for %s", source)
            return StringIO(raw_content) if raw_content else None
        return None

    def attached_source(self, unused_context, source):
        raw_content = source.data
        return StringIO(raw_content) if raw_content else None

    def value(self, context=None):
        context = self.context if context is None else context
        source = context.src
        if isinstance(source, string_types):
            return self.library_source(context, source)
        elif IFile.providedBy(source):
            return self.attached_source(context, source)
        return None


@component.adapter(INTITranscript)
@interface.implementer(IContainersValue)
class _TranscriptContainerIdValue(_AssetContainerIdValue):
    pass
