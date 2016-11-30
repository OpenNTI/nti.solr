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

from nti.contentlibrary.indexed_data import get_library_catalog

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.courses.common import get_course_packages

from nti.contenttypes.presentation.interfaces import INTITranscript

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.traversal.traversal import find_interface

from nti.solr.interfaces import ITranscriptSource

def get_content_package_from_ntiids(ntiids):
	try:
		from nti.contenttypes.courses.interfaces import ICourseInstance
		from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

		result = None
		for ntiid in ntiids or ():
			obj = find_object_with_ntiid(ntiid)
			if ICourseCatalogEntry.providedBy(obj) or ICourseInstance.providedBy(obj):
				packages = get_course_packages(obj)
				result = packages[0] if packages else None  # pick first
				if result is not None:
					break
			elif IContentPackage.providedBy(obj):
				result = obj
				break
			elif IContentUnit.providedBy(obj):
				result = find_interface(obj, IContentPackage, strict=False)
				if result is not None:
					break
		return result
	except ImportError:
		return None

def get_item_content_package(item):
	catalog = get_library_catalog()
	entries = catalog.get_containers(item)
	result = get_content_package_from_ntiids(entries) if entries else None
	return result

@component.adapts(INTITranscript)
@interface.implementer(ITranscriptSource)
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
			if package is None:
				package = get_item_content_package(context)
			try:
				raw_content = package.read_contents_of_sibling_entry(src)
			except Exception:
				logger.exception("Cannot read contents for %s", src)
		return StringIO(raw_content) if raw_content else None
	