#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.contentsearch.interfaces import IContentUnitSearchHit

from nti.contentsearch.search_hits import ContentUnitSearchHit

from nti.solr.adapters import _default_search_hit_adapter


@interface.implementer(IContentUnitSearchHit)
def _contentunit_search_hit_adapter(obj, result):
    return _default_search_hit_adapter(obj, result, ContentUnitSearchHit())
