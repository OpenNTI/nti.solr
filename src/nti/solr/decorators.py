#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re

from zope import component

from nti.contentsearch.interfaces import ISearchFragment

from nti.externalization.singleton import SingletonDecorator

from nti.solr.query import hl_removeEncodedHTML

@component.adapter(ISearchFragment)
class _SearchFragmentDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, original, external):
		query = original.__parent__.Query
		if hl_removeEncodedHTML(query):
			for idx, match in enumerate(original.Matches or ()):
				match = re.sub("&lt;.*&gt;", '', match)
				external['Matches'][idx] = match
