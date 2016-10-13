#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.solr.interfaces import ICoreCatalog

@interface.implementer(ICoreCatalog)
class CoreCatalog(object):
    pass
