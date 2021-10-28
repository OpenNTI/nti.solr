#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

import unittest

from nti.solr.decorators import _SearchFragmentDecorator

from nti.solr.tests import SOLRTestLayer


class TestDecorators(unittest.TestCase):

    layer = SOLRTestLayer

    def test_fragment_1(self):
        s = u'how our chemical messengers are synthesized and secreted from the secretory <hit>cell</hit>. Now'
        assert_that(_SearchFragmentDecorator.sanitize(s), is_(s))

    def test_fragment_2(self):
        s = u"The function of one type of parathyroid <hit>cells</hit> and other <hit>cells</hit> in the body"
        assert_that(_SearchFragmentDecorator.sanitize(s), is_(s))

    def test_fragment_4(self):
        s = u'//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html><head></head><body>The Adaptive Immune Response: T <hit>Lymphocytes</hit> and Their Functional'
        assert_that(_SearchFragmentDecorator.sanitize(s),
                    is_(u"The Adaptive Immune Response: T <hit>Lymphocytes</hit> and Their Functional"))

    def test_wrapped_anchors(self):
        # We do not handle this case
        # With nti.contentfragments 1.9, links are in markup
        hit = u' <a href="http://en.wikipedia.org/wiki/Wort"><span>wort</span></a> is boiled with <a href="http://en.wikipedia.org/wiki/Hops"><span><hit>hops</span></a></hit> (and other'
        assert_that(_SearchFragmentDecorator.sanitize(hit),
                    is_(u'[wort](http://en.wikipedia.org/wiki/Wort) is boiled with [hops](http://en.wikipedia.org/wiki/Hops)\n(and other'))

    def test_wowza(self):
        # With nti.contentfragments 1.9, `p` tags end up as newlines
        hit = u"<html><body>/W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\"><html><head>         </head> <body>  realtitle <p></p><p>  realtitle </p><p></p> <h2>partitle</h2><h2>partitle</h2><h1>jz title</h1><h1>jz title</h1><a></a> <p>imaparagraph</p> <h1>jz title</h1><a></a> <p><hit>wowza</hit> <hit>wowza</hit></p> <a></a> <p><hit>wowza</hit></p> <a></a> <p>adlk;fj;</p> <a></a> <p>w;k</p>  </body></html>"
        assert_that(_SearchFragmentDecorator.sanitize(hit),
                    is_(u'realtitle\n\nrealtitle\n\n## partitle\n\n## partitle\n\n# jz title\n\n# jz title\n\nimaparagraph\n\n# jz title\n\n<hit>wowza</hit> <hit>wowza</hit>\n\n<hit>wowza</hit>\n\nadlk;fj;\n\nw;k'))
