#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that

import unittest

from nti.solr.termextract import extract_key_words

from nti.solr.tests import SOLRTestLayer


class TestTermExtract(unittest.TestCase):

    layer = SOLRTestLayer

    def test_extract_key_words(self):
        content = """
        Although he is known to be a violent fighter, Kenpachi's actions tend to be for the best. 
        Kenpachi lives for battle, and enjoys a good fight more than anything. 
        He even holds back in an effort to make any fight last longer.
        He claims injury and death are nothing but the price one pays for a good fight. 
        Despite his tendency to be brutal, Kenpachi usually stops a fight if his opponent is too injured to fight back, 
        claiming he is not interested in fighting "weaklings who can't fight anymore", 
        and he does not feel obligated to deal a death blow to anyone who cannot fight any longer.
        However, he will unhesitatingly kill his opponent if they refuse to end their fight, 
        such as during his battles with Kaname Tosen and Nnoitra Gilga. 
        He also takes his title as Kenpachi seriously, telling Gremmy Thoumeaux that there is 
        nothing the latter can create that he cannot cut because the power his title implies is 
        not to be taken lightly.
        """
        words = extract_key_words(content, max_words=6,
                                  blacklist=('nnoitra', 'thoumeaux', 'title'))
        assert_that(words,
                    is_([u'battle', u'blow', u'death', u'fight', u'kenpachi', u'opponent']))
