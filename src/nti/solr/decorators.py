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

from nti.contentsearch.interfaces import ISearchFragment

from nti.externalization.singleton import SingletonDecorator

from nti.solr.query import hl_removeEncodedHTML

@component.adapter(ISearchFragment)
class _SearchFragmentDecorator(object):

	__metaclass__ = SingletonDecorator

	@classmethod
	def sanitize(cls, raw):
		try:
			raw = re.sub(r'\\/', '/', to_unicode(raw))
			parser = HTMLParser(tree=treebuilders.getTreeBuilder("lxml"),
						   		namespaceHTMLElements=False)
			doc = parser.parse(raw)
			text = []
			for element in doc.iter("*"):
				if element.tag == 'em':
					text.append('<em>')
				if element.text is not None:
					text.append(element.text)
				if element.tag == 'em':
					text.append('</em>')
			raw = ''.join(text)
		except Exception:
			pass
		return raw

	def decorateExternalObject(self, original, external):
		query = original.__parent__.Query
		if hl_removeEncodedHTML(query):
			for idx, match in enumerate(original.Matches or ()):
				match = self.sanitize(match)
				external['Matches'][idx] = match
