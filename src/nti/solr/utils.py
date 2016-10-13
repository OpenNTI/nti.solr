#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import component

from zope.interface.interfaces import IMethod

from zope.intid.interfaces import IIntIds

from nti.contentlibrary.indexed_data import get_library_catalog

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.contentprocessing.keyword import extract_key_words

from nti.contenttypes.courses.common import get_course_packages

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.solr.termextract import extract_key_words as term_extract_key_words

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

def get_keywords(content, lang='en'):
	keywords = extract_key_words(content, lang='en')
	if not keywords:
		keywords = term_extract_key_words(content, lang=lang)
	return keywords

def document_creator(obj, factory, provided):
	result = factory()
	for k, v in provided.namesAndDescriptions(all=True):
		__traceback_info__ = k, v
		if IMethod.providedBy(v):
			continue
		value_interface = v.queryTaggedValue('__solr_value_interface__')
		if value_interface is None:
			continue
		adapted = value_interface(obj, None)
		if adapted is not None:
			value = adapted.value()
			setattr(result, k, value)
	return result

def object_finder(doc_id):
	if doc_id is None:
		return None
	intids = component.getUtility(IIntIds)
	try:
		doc_id = int(doc_id)
		return intids.queryObject(doc_id)
	except (ValueError, TypeError):
		pass
	if isinstance(doc_id, six.string_types):
		return find_object_with_ntiid(doc_id)
	return None
