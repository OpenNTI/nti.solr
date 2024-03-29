#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

import unittest

from zope.dottedname import resolve as dottedname

from nti.solr.presentation.tests import HAS_PRESENTATION


@unittest.skipIf(not HAS_PRESENTATION, "")
class TestInterfaces(unittest.TestCase):

    def test_import_interfaces(self):
        dottedname.resolve('nti.solr.presentation.interfaces')
