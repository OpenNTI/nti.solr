#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.property.property import alias

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from nti.solr.interfaces import ISOLR


@interface.implementer(ISOLR)
class SOLR(SchemaConfigured):
    createDirectFieldProperties(ISOLR)

    url = alias('URL')
    timeout = alias('Timeout')
