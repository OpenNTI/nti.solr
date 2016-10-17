#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import functools

from zope import interface

from zope.component.zcml import utility

from zope.configuration import fields

from nti.schema.field import Int

from nti.solr.interfaces import ISOLR

from nti.solr.model import SOLR

class IRegisterSOLR(interface.Interface):
	url = fields.TextLine(title="SOLR url", required=True)
	name = fields.TextLine(title="optional registration name", required=False)
	timeout = Int(title="timeout", required=False)
	
def registerSOLR(_context, url, timeout=None, name=u''):
	assert not timeout or timeout > 0, 'Invalid SOLR timeout'
	url = url[0:-1] if url.endswith('/') else url
	factory = functools.partial(SOLR, URL=url, Timeout=timeout or None)
	utility(_context, provides=ISOLR, factory=factory, name=name)
