#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.schema.field import IndexedIterable
from nti.schema.field import Text as ValidText
from nti.schema.field import DecodingValidTextLine as ValidTextLine

from nti.solr.interfaces import tagField
from nti.solr.interfaces import ITextField
from nti.solr.interfaces import IStringValue
from nti.solr.interfaces import IAttributeValue
from nti.solr.interfaces import IMetadataDocument


class IUsernameValue(IAttributeValue):
    """
    Adapter interface to get the username value from a given object
    """


class IAliasValue(IAttributeValue):
    """
    Adapter interface to get the alias value from a given object
    """


class IRealnameValue(IAttributeValue):
    """
    Adapter interface to get the realname value from a given object
    """


class IEmailValue(IAttributeValue):
    """
    Adapter interface to get the email value from a given object
    """


class IProfessionalTitleValue(IAttributeValue):
    """
    Adapter interface to get the professional titles from a given entity object
    """


class IProfessionalCompanyValue(IAttributeValue):
    """
    Adapter interface to get the professional companies from a given entity object
    """


class IProfessionalDescriptionValue(IAttributeValue):
    """
    Adapter interface to get the professional descriptions from a given entity object
    """


class IEducationSchoolValue(IAttributeValue):
    """
    Adapter interface to get the education schools from a given entity object
    """


class IEducationDegreeValue(IAttributeValue):
    """
    Adapter interface to get the education degrees from a given entity object
    """


class IEducationDescriptionValue(IAttributeValue):
    """
    Adapter interface to get the education descriptions from a given entity object
    """


class ISocialURLValue(IAttributeValue):
    """
    Adapter interface to get the social URLs from a given entity object
    """


class IAboutValue(IStringValue):
    """
    Adapter interface to get the about value from a given entity object
    """

class ILocationValue(IAttributeValue):
    """
    Adapter interface to get the location value from a given object
    """

class IRoleValue(IAttributeValue):
    """
    Adapter interface to get the role value from a given object
    """


class IEntityDocument(IMetadataDocument):

    username = IndexedIterable(title=u'The username identifiers',
                               required=False,
                               value_type=ValidTextLine(title=u"The username"),
                               min_length=1)

    alias = ValidTextLine(title=u'The alias', required=False)

    email = ValidTextLine(title=u'The username', required=False)

    realname = ValidTextLine(title=u'The realname', required=False)

    about_en = ValidText(title=u'The about statement', required=False)
    
    role = ValidTextLine(title=u'The role', required=False)
    
    location = ValidTextLine(title=u'The location', required=False)

    education_school = IndexedIterable(title=u'The school names',
                                       required=False,
                                       value_type=ValidTextLine(
                                           title=u"The school name"),
                                       min_length=0)

    education_degree = IndexedIterable(title=u'The school degrees',
                                       required=False,
                                       value_type=ValidTextLine(title=u"The school degree"),
                                       min_length=0)

    education_description = IndexedIterable(title=u'The education descriptions',
                                            required=False,
                                            value_type=ValidText(
                                                title=u"The description"),
                                            min_length=0)

    professional_description = IndexedIterable(title=u'The professional company descriptions',
                                               required=False,
                                               value_type=ValidText(title=u"The description"),
                                               min_length=0)

    professional_title = IndexedIterable(title=u'The company names',
                                         required=False,
                                         value_type=ValidTextLine(title=u"The company name"),
                                         min_length=0)

    professional_company = IndexedIterable(title=u'The company names',
                                           required=False,
                                           value_type=ValidTextLine(title=u"The company name"),
                                           min_length=0)

    social_url = IndexedIterable(title=u'The social URLS',
                                 required=False,
                                 value_type=ValidTextLine(title=u"The url"),
                                 min_length=0)

tagField(IEntityDocument['email'], True, IEmailValue)

tagField(IEntityDocument['alias'], True, IAliasValue, type_=u'text_lower')

tagField(IEntityDocument['realname'], True, IRealnameValue, type_=u'text_lower')

tagField(IEntityDocument['username'], True, IUsernameValue, True)

tagField(IEntityDocument['role'], True, IRoleValue, True, type_=u'text_lower')

tagField(IEntityDocument['location'], True, ILocationValue, True, type_=u'text_lower')

tagField(IEntityDocument['social_url'], True, ISocialURLValue, True)

tagField(IEntityDocument['about_en'], False, IAboutValue, provided=ITextField)

tagField(IEntityDocument['education_school'], True,
         IEducationSchoolValue, True, type_=u'text_lower', provided=ITextField)

tagField(IEntityDocument['education_degree'], True,
         IEducationDegreeValue, True, type_=u'text_lower', provided=ITextField)

tagField(IEntityDocument['education_description'], True,
         IEducationDescriptionValue, True, type_=u'text_lower', provided=ITextField)

tagField(IEntityDocument['professional_title'], True,
         IProfessionalTitleValue, True, type_=u'text_lower', provided=ITextField)

tagField(IEntityDocument['professional_company'], True,
         IProfessionalCompanyValue, True, type_=u'text_lower', provided=ITextField)

tagField(IEntityDocument['professional_description'], True,
         IProfessionalDescriptionValue, True, type_=u'text_lower', provided=ITextField)
