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

from zope import interface

from zope.mimetype.interfaces import IContentTypeAware

from nti.base.interfaces import ICreated
from nti.base.interfaces import ICreatedTime
from nti.base.interfaces import ILastModified

from nti.contenttypes.presentation.media import NTITranscript

from nti.dataserver.users.interfaces import ICompleteUserProfile

from nti.dataserver.users.users import User

from nti.dataserver.users.user_profile import Education
from nti.dataserver.users.user_profile import ProfessionalPosition

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IInReplyToValue
from nti.solr.interfaces import ISocialURLValue
from nti.solr.interfaces import ISharedWithValue
from nti.solr.interfaces import ICreatedTimeValue
from nti.solr.interfaces import ILastModifiedValue
from nti.solr.interfaces import IEducationDegreeValue
from nti.solr.interfaces import IEducationSchoolValue
from nti.solr.interfaces import IProfessionalTitleValue
from nti.solr.interfaces import IProfessionalCompanyValue
from nti.solr.interfaces import IEducationDescriptionValue
from nti.solr.interfaces import IProfessionalDescriptionValue

from nti.solr.tests import SOLRTestLayer


class TestAdpaters(unittest.TestCase):

    layer = SOLRTestLayer

    def test_creator(self):

        @interface.implementer(ICreated)
        class Created(object):
            creator = 'ichigo'

        value = ICreatorValue(Created()).value()
        assert_that(value, is_('ichigo'))

    def test_mimetype(self):

        @interface.implementer(IContentTypeAware)
        class Created(object):
            mimeType = 'text/x-python'

        value = IMimeTypeValue(Created()).value()
        assert_that(value, is_('text/x-python'))

    def test_ntiid(self):

        @interface.implementer(IContentTypeAware)
        class Created(object):
            ntiid = 'foo'

        value = INTIIDValue(Created()).value()
        assert_that(value, is_('foo'))

    def test_created_last_mod_times(self):

        @interface.implementer(ICreatedTime, ILastModified)
        class Created(object):
            lastModified = createdTime = 1475604175.0

        obj = Created()
        for iface in (ICreatedTimeValue, ILastModifiedValue):
            value = iface(obj).value()
            assert_that(value, is_('2016-10-04T18:02:55Z'))

    def test_sharedWith(self):

        class Created(object):
            sharedWith = ("ichigo", 'Aizen')

        value = ISharedWithValue(Created()).value()
        assert_that(value, is_(('ichigo', 'aizen')))

    def test_inReplyTo(self):

        class Created(object):
            inReplyTo = "Aizen"

        value = IInReplyToValue(Created()).value()
        assert_that(value, is_('aizen'))

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
        
    def test_transcript(self):
        transcript = NTITranscript()
        transcript.ntiid = u"tag:nextthought.com,2011-10:NTI-NTITranscript-system_A10319BA.0"
        assert_that(IIDValue(transcript).value(),
                    is_('19701S-system-ntitranscript#tag:nextthought.com,2011-10:NTI-NTITranscript-system_A10319BA.0'))
        