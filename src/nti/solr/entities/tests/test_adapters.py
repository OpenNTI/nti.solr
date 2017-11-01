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

from nti.dataserver.users.interfaces import ICompleteUserProfile

from nti.dataserver.users.users import User

from nti.dataserver.users.user_profile import Education
from nti.dataserver.users.user_profile import ProfessionalPosition

from nti.solr.entities.interfaces import ISocialURLValue
from nti.solr.entities.interfaces import IEducationDegreeValue
from nti.solr.entities.interfaces import IEducationSchoolValue
from nti.solr.entities.interfaces import IProfessionalTitleValue
from nti.solr.entities.interfaces import IProfessionalCompanyValue
from nti.solr.entities.interfaces import IEducationDescriptionValue
from nti.solr.entities.interfaces import IProfessionalDescriptionValue

from nti.solr.tests import SOLRTestLayer


class TestAdapters(unittest.TestCase):

    layer = SOLRTestLayer

    def test_entities(self):
        user = User(u"ichigo@bleach.org")
        prof = ICompleteUserProfile(user)
        prof.alias = u'Ichigo'
        prof.realname = u'Ichigo Kurosaki'

        prof.twitter = 'https://twitter.com/ichigo'
        prof.positions = [ProfessionalPosition(startYear=1998,
                                               endYear=2009,
                                               companyName=u'NTI',
                                               title=u'Developer',
                                               description=u'Software Developer')]
        prof.education = [Education(startYear=1994,
                                    endYear=1997,
                                    school=u'OU',
                                    degree=u'Master',
                                    description=u'Computer Science')]

        value = ISocialURLValue(user).value()
        assert_that(value, is_(('https://twitter.com/ichigo',)))

        value = IProfessionalTitleValue(user).value()
        assert_that(value, is_(('Developer',)))

        value = IProfessionalCompanyValue(user).value()
        assert_that(value, is_(('NTI',)))

        value = IProfessionalDescriptionValue(user).value()
        assert_that(value, is_(('Software Developer',)))

        value = IEducationDegreeValue(user).value()
        assert_that(value, is_(('Master',)))

        value = IEducationSchoolValue(user).value()
        assert_that(value, is_(('OU',)))

        value = IEducationDescriptionValue(user).value()
        assert_that(value, is_(('Computer Science',)))
