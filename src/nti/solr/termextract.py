#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import interface

from nti.common.string import to_unicode

from nti.contentprocessing.content_utils import tokenize_content

from nti.contentprocessing.keyword import term_extract_key_words

from nti.contentprocessing.keyword.interfaces import ITermExtractFilter


@interface.implementer(ITermExtractFilter)
class _DefaultKeyWordFilter(object):

    def __init__(self, single_strength_min_occur=3, max_limit_strength=2):
        self.max_limit_strength = max_limit_strength
        self.single_strength_min_occur = single_strength_min_occur

    def __call__(self, word, occur, strength):
        result = (strength == 1 and occur >= self.single_strength_min_occur) \
              or (strength <= self.max_limit_strength)
        return bool(result and len(word) > 1)


def extract_key_words(content, max_words=10, lang='en',
                      filtername='solr', blacklist=()):
    """
    extract key words for the specified list of tokens

    :param tokenized_words: List of tokens (words)
    :param max_words: Max number of words to return
    """
    keywords = set()
    if isinstance(content, six.string_types):
        content = tokenize_content(content, lang=lang)
    blacklist = blacklist or ()
    records = term_extract_key_words(content, lang=lang, filtername=filtername)
    for r in records:
        word = r.token
        terms = getattr(r, 'terms', ())
        word = terms[0] if terms else word  # pick the first word
        word = to_unicode(word.lower())
        if word not in blacklist:
            keywords.add(word)
            if len(keywords) >= max_words:
                break
    return sorted(keywords)
