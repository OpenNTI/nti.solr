#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six

from zope import component
from zope import interface

from zope.component.hooks import getSite

from nti.base._compat import text_

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IUseNTIIDAsExternalUsername

from nti.dataserver.users.common import user_creation_sitename

from nti.dataserver.users.interfaces import IUserProfile
from nti.dataserver.users.interfaces import IAboutProfile
from nti.dataserver.users.interfaces import IFriendlyNamed
from nti.dataserver.users.interfaces import IEducationProfile
from nti.dataserver.users.interfaces import ISocialMediaProfile
from nti.dataserver.users.interfaces import IProfessionalProfile
from nti.dataserver.users.interfaces import ICompleteUserProfile

from nti.ntiids.oids import to_external_ntiid_oid

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.entities import ENTITIES_CATALOG

from nti.solr.entities.interfaces import IRoleValue
from nti.solr.entities.interfaces import IAboutValue 
from nti.solr.entities.interfaces import IAliasValue
from nti.solr.entities.interfaces import IEmailValue
from nti.solr.entities.interfaces import ILocationValue
from nti.solr.entities.interfaces import IRealnameValue
from nti.solr.entities.interfaces import IUsernameValue
from nti.solr.entities.interfaces import IEntityDocument
from nti.solr.entities.interfaces import ISocialURLValue
from nti.solr.entities.interfaces import IEducationDegreeValue
from nti.solr.entities.interfaces import IEducationSchoolValue
from nti.solr.entities.interfaces import IProfessionalTitleValue
from nti.solr.entities.interfaces import IProfessionalCompanyValue
from nti.solr.entities.interfaces import IEducationDescriptionValue
from nti.solr.entities.interfaces import IProfessionalDescriptionValue
from nti.solr.entities.interfaces import ICustomSOLREntityDocument

from nti.solr.interfaces import ISiteValue
from nti.solr.interfaces import ICoreCatalog 
from nti.solr.interfaces import IEntityCatalog

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument

from nti.solr.utils import document_creator
from nti.solr.utils import resolve_content_parts

logger = __import__('logging').getLogger(__name__)


class _BasicAttributeValue(object):

    field = None
    interface = None

    def __init__(self, context=None, _=None):
        self.context = context

    def value(self, context=None):
        context = self.context if context is None else context
        profile = self.interface(context, None) # pylint: disable=not-callable
        result = getattr(profile, self.field, None)
        if isinstance(result, six.string_types):
            result = text_(result)
        return result


@component.adapter(IEntity)
@interface.implementer(IUsernameValue)
class _DefaultUsernameValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        if IUseNTIIDAsExternalUsername.providedBy(context):
            result = to_external_ntiid_oid(context)
        else:
            result = getattr(context, 'username', None)
            result = result.lower() if result else None
        return (text_(result),) if result else ()


@component.adapter(IEntity)
@interface.implementer(IEmailValue)
class _DefaultEmailValue(_BasicAttributeValue):

    field = 'email'
    interface = IUserProfile

    def value(self, context=None):
        result = _BasicAttributeValue.value(self, context)
        return result.lower() if result else None


@component.adapter(IUser)
@interface.implementer(ISiteValue)
class _DefaultUserSiteValue(object):

    def __init__(self, context=None, unused_default=None):
        self.context = context
        
    def value(self, context=None):
        context = self.context if context is None else context
        result = user_creation_sitename(context) or getSite().__name__
        return result


@component.adapter(IEntity)
@interface.implementer(IAliasValue)
class _DefaultAliasValue(_BasicAttributeValue):
    field = 'alias'
    interface = IFriendlyNamed


@component.adapter(IEntity)
@interface.implementer(IRealnameValue)
class _DefaultRealnameValue(_BasicAttributeValue):
    field = 'realname'
    interface = IFriendlyNamed


@component.adapter(IEntity)
@interface.implementer(IRoleValue)
class _DefaultRoleValue(_BasicAttributeValue):
    field = 'role'
    interface = ICompleteUserProfile


@component.adapter(IEntity)
@interface.implementer(ILocationValue)
class _DefaultLocationValue(_BasicAttributeValue):
    field = 'location'
    interface = IUserProfile


@component.adapter(IEntity)
@interface.implementer(IProfessionalTitleValue)
class _DefaultProfessionalTitleValue(_BasicAttributeValue):

    field = 'positions'
    interface = IProfessionalProfile

    def value(self, context=None):
        source = _BasicAttributeValue.value(self, context) or ()
        return tuple(text_(x.title) for x in source if x.title) if source else ()


@component.adapter(IEntity)
@interface.implementer(IProfessionalCompanyValue)
class _DefaultProfessionalCompanyValue(_DefaultProfessionalTitleValue):

    def value(self, context=None):
        source = _BasicAttributeValue.value(self, context) or ()
        return tuple(text_(x.companyName) for x in source if x.companyName) if source else ()


@component.adapter(IEntity)
@interface.implementer(IProfessionalDescriptionValue)
class _DefaultProfessionalDescriptionValue(_DefaultProfessionalTitleValue):

    def value(self, context=None):
        source = _BasicAttributeValue.value(self, context) or ()
        return tuple(text_(x.description) for x in source if x.description) if source else ()


@component.adapter(IEntity)
@interface.implementer(IEducationDegreeValue)
class _DefaultEducationDegreeValue(_BasicAttributeValue):

    field = 'education'
    interface = IEducationProfile

    def value(self, context=None):
        source = _BasicAttributeValue.value(self, context) or ()
        return tuple(text_(x.degree) for x in source if x.degree) if source else ()


@component.adapter(IEntity)
@interface.implementer(IEducationSchoolValue)
class _DefaultEducationSchoolValue(_DefaultEducationDegreeValue):

    def value(self, context=None):
        source = _BasicAttributeValue.value(self, context) or ()
        return tuple(text_(x.school) for x in source if x.school) if source else ()


@component.adapter(IEntity)
@interface.implementer(IEducationDescriptionValue)
class _DefaultEducationDescriptionValue(_DefaultEducationDegreeValue):

    def value(self, context=None):
        source = _BasicAttributeValue.value(self, context) or ()
        return tuple(text_(x.description) for x in source if x.description) if source else ()


@component.adapter(IEntity)
@interface.implementer(ISocialURLValue)
class _DefaultSocialURLValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        profile = ISocialMediaProfile(context, None)
        if profile is not None:
            result = {profile.twitter, profile.facebook, profile.linkedIn}
            return tuple(text_(x.lower()) for x in result if x)
        return ()


@component.adapter(IEntity)
@interface.implementer(IAboutValue)
class _DefaultAboutValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        profile = IAboutProfile(context, None)
        if profile is not None:
            return resolve_content_parts(profile.about)
        return None


@interface.implementer(IEntityDocument)
class EntityDocument(MetadataDocument):
    createDirectFieldProperties(IEntityDocument)

    mimeType = mime_type = 'application/vnd.nextthought.solr.entitydocument'


@component.adapter(IEntity)
@interface.implementer(IEntityDocument)
def _EntityDocumentCreator(obj, factory=EntityDocument):
    return document_creator(obj, factory=factory, provided=IEntityDocument)


@component.adapter(IEntity)
@interface.implementer(ICoreCatalog)
def _entity_to_catalog(unused_obj):
    return component.getUtility(ICoreCatalog, name=ENTITIES_CATALOG)


@interface.implementer(IEntityCatalog)
class EntitiesCatalog(MetadataCatalog):

    name = ENTITIES_CATALOG

    @property
    def document_interface(self):
        document_interface = component.queryUtility(ICustomSOLREntityDocument)
        return document_interface if document_interface else IEntityDocument

    def build_from_search_query(self, query, **kwargs):  # pylint: disable=arguments-differ
        term, fq, params = MetadataCatalog.build_from_search_query(self, query, **kwargs)
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None):
        types = self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        commit = self.auto_commit if commit is None else bool(commit)
        self.client.delete(q=q, commit=commit)
    reset = clear
