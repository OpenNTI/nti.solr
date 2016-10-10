#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.contentlibrary.indexed_data import get_library_catalog

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.courses.common import get_course_packages

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.traversal.traversal import find_interface

def get_content_package_from_ntiids(ntiids):
	result = None
	for ntiid in ntiids or ():
		obj = find_object_with_ntiid(ntiid)
		if ICourseCatalogEntry.providedBy(obj) or ICourseInstance.providedBy(obj):
			packages = get_course_packages(obj)
			result = packages[0] if packages else None
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

def get_item_content_package(item):
	catalog = get_library_catalog()
	entries = catalog.get_containers(item)
	result = get_content_package_from_ntiids(entries) if entries else None
	return result
