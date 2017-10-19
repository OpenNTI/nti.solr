#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.property.property import alias

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

from nti.solr.interfaces import ISOLR

logger = __import__('logging').getLogger(__name__)


@interface.implementer(ISOLR)
class SOLR(SchemaConfigured):
    createDirectFieldProperties(ISOLR)

    url = alias('URL')
    timeout = alias('Timeout')
