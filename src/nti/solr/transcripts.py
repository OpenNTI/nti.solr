#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.contenttypes.presentation.interfaces import INTITranscript

from nti.solr.interfaces import IIDValue

@component.adapts(INTITranscript)
@interface.implementer(IIDValue)
class _TranscriptIDValue(object):

	def __init__(self, context):
		self.context = context

	def value(self, context=None):
		context = self.context if context is None else context
		return context.ntiid
