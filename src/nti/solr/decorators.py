#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re

from html5lib import HTMLParser
from html5lib import treebuilders

from zope import component

from nti.common.string import to_unicode

from nti.contentsearch.interfaces import ISearchHit, ITranscriptSearchHit
from nti.contentsearch.interfaces import ISearchFragment

from nti.externalization.interfaces import StandardExternalFields

from nti.externalization.oids import to_external_ntiid_oid

from nti.externalization.singleton import SingletonDecorator

from nti.solr.query import hl_removeEncodedHTML

NTIID = StandardExternalFields.NTIID
CONTAINER_ID = StandardExternalFields.CONTAINER_ID

@component.adapter(ISearchFragment)
class _SearchFragmentDecorator(object):

	__metaclass__ = SingletonDecorator

	@classmethod
	def sanitize(cls, raw, tag='em'):
		"""
		Clean any HTML by parsing the DOM elements getting their text 
		and only leaving only the hightlighting element tags
		"""
		try:
			text = []
			end_ele = '</%s>' % tag
			start_ele = '<%s>' % tag
			parser = HTMLParser(tree=treebuilders.getTreeBuilder("lxml"),
						   		namespaceHTMLElements=False)
			doc = parser.parse(raw)
			for element in doc.iter("*"):
				if element.tag == tag:
					text.append(start_ele)
				if element.text is not None:
					text.append(element.text)
				if element.tag == tag:
					text.append(end_ele)
			raw = ''.join(text)
		except Exception as e:
			logger.warn("Could not parse %s. %s", raw, e)
		return raw
	
	@classmethod
	def split_and_sanitize(cls, raw, tag='em'):
		result = []
		prior = None
		end_ele = '</%s>' % tag
		start_ele = '<%s>' % tag
		# clean raw string and make it unicode
		raw = re.sub(r'\\/', '/', to_unicode(raw))
		# split by enclosing element
		for split in re.split(r'(%s)' % start_ele, raw):
			if split != start_ele:
				if prior == start_ele:
					# process highlighted element (e.g. <em>cell</em>)
					idx = split.find(end_ele)
					end_idx = idx+len(end_ele)
					enclosed ='%s%s' % (prior, split[:end_idx])
					result.append(cls.sanitize(enclosed))
					# process rest
					split = split[end_idx:]
					# add any extra spaces for next clean up
					m = re.search(r'[^\s]', split)
					if m and m.start() != 0:
						result.append(split[:m.start()])
						split = split[m.start():]
				if split:
					result.append(cls.sanitize(split))
			prior = split
		return ''.join(result)

	def decorateExternalObject(self, original, external):
		hit = original.__parent__
		# trascript hits are plain text
		if 		not ITranscriptSearchHit.providedBy(hit) \
			and hl_removeEncodedHTML(hit.Query):
			for idx, match in enumerate(original.Matches or ()):
				match = self.split_and_sanitize(match)
				external['Matches'][idx] = match

@component.adapter(ISearchHit)
class _SearchHitDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, original, external):
		target = original.Target
		containers = external.get('Containers') or ()
		if CONTAINER_ID not in external and len(containers) == 1:
			external[CONTAINER_ID] = containers[0]
		if not external.get(NTIID):
			external[NTIID] = to_external_ntiid_oid(target)

