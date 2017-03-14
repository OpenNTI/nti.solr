#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

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
        s = 'how our chemical messengers are synthesized and secreted from the secretory <em>cell</em>. Now'
        assert_that(_SearchFragmentDecorator.sanitize(s), is_(s))

    def test_fragment_2(self):
        s = "The function of one type of parathyroid <em>cells</em> and other <em>cells</em> in the body"
        assert_that(_SearchFragmentDecorator.sanitize(s), is_(s))

    def test_fragment_4(self):
        s = u'//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html><head>      </head><body>The Adaptive Immune Response: T <em>Lymphocytes</em> and Their Functional'
        assert_that(_SearchFragmentDecorator.sanitize(s),
                    is_(u"The Adaptive Immune Response: T <em>Lymphocytes</em> and Their Functional"))

    def test_wowza(self):
        hit = "<html><body>/W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\"><html><head>         </head> <body>  realtitle <p></p><p>  realtitle </p><p></p> <h2>partitle</h2><h2>partitle</h2><h1>jz title</h1><h1>jz title</h1><a></a> <p>imaparagraph</p> <h1>jz title</h1><a></a> <p><em>wowza</em> <em>wowza</em></p> <a></a> <p><em>wowza</em></p> <a></a> <p>adlk;fj;</p> <a></a> <p>w;k</p>  </body></html>"
        assert_that(_SearchFragmentDecorator.sanitize(hit),
                    is_(u'realtitle   realtitle  partitlepartitlejz titlejz title imaparagraph jz title <em>wowza</em> <em>wowza</em>  <em>wowza</em>  adlk;fj;  w;k'))
