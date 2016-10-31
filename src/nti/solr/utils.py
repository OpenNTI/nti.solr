#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re
import six

from zope import component

from zope.interface.interfaces import IMethod

from zope.intid.interfaces import IIntIds

from nti.common.string import to_unicode

from nti.contentlibrary.indexed_data import get_library_catalog

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.contentprocessing.content_utils import tokenize_content

from nti.contentprocessing.keyword import extract_key_words

from nti.ntiids.ntiids import find_object_with_ntiid, is_valid_ntiid_string

from nti.schema.interfaces import find_most_derived_interface

from nti.solr.interfaces import IStringValue
from nti.solr.interfaces import ICoreDocument

from nti.solr.termextract import extract_key_words as term_extract_key_words

from nti.traversal.traversal import find_interface

# assets

def get_content_package_from_ntiids(ntiids):
	try:
		from nti.contenttypes.courses.common import get_course_packages
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

# content

def resolve_content_parts(data):
	result = []
	data = [data] if isinstance(data, six.string_types) else data
	for item in data or ():
		adapted = IStringValue(item, None)
		if adapted is not None:
			result.append(adapted.value())
	result = u'\n'.join(x for x in result if x is not None)
	return result

def get_content(text=None, lang="en"):
	if not text or not isinstance(text, six.string_types):
		result = u''
	else:
		text = to_unicode(text)
		result = tokenize_content(text, lang)
		result = ' '.join(result) if result else text
	return result

def get_keywords(content, lang='en'):
	keywords = extract_key_words(content, lang='en')
	if not keywords:
		keywords = term_extract_key_words(content, lang=lang)
	return keywords

# documents

def document_creator(obj, factory, provided=None):
	result = factory()
	if provided is None:
		provided = find_most_derived_interface(result, ICoreDocument)
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

_k_pattern = re.compile('(.*)!=(.*)', re.UNICODE | re.IGNORECASE)
def normalized_key(doc_id):
	m = _k_pattern.match(doc_id)
	if m is not None:
		return m.groups()[1]
	return doc_id

def object_finder(doc_id, intids=None):
	doc_id = normalized_key(doc_id)
	if is_valid_ntiid_string(doc_id):
		return find_object_with_ntiid(doc_id)
	else:
		intids = component.getUtility(IIntIds) if intids is None else intids
		return intids.queryObject(int(doc_id))

_f_pattern = re.compile('(.*)(_[a-z]{2})$', re.UNICODE | re.IGNORECASE)
def normalize_field(name):
	m = _f_pattern.match(name)
	if m is not None:
		return m.groups()[0]
	return name
