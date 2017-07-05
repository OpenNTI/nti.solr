#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re
import six

from nti.solr.lucene.grammar import expression


def lucene_escape(s):
    s = s if isinstance(s, six.string_types) else str(s)
    return re.sub(r'([\+\-\!\(\)\{\}\[\]\^\"\~\*\?\:])', r'\\\g<1>', s)
escape = lucene_escape

phrase_search = re.compile(r'"(?P<text>.*?)"')
prefix_search = re.compile(r'(?P<text>[^ \t\r\n*]+)[*](?= |$|\\)')


def is_phrase_search(term):
    return phrase_search.match(term) is not None if term else False


def is_prefix_search(term):
    return prefix_search.match(term) is not None if term else False


def is_valid_query(term):
    try:
        return bool(expression.parseString(term, parseAll=True))
    except Exception:
        return False
