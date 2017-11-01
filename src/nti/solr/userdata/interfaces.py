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
from nti.solr.interfaces import ITagsValue
from nti.solr.interfaces import ITextField
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import ISuggestField
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IAttributeValue
from nti.solr.interfaces import IMetadataDocument


class IChannelValue(IAttributeValue):
    """
    Adapter interface to get the channel value from a given object
    """


class IExplanationValue(IAttributeValue):
    """
    Adapter interface to get the explanation value from a given object
    """


class IReplacementContentValue(IAttributeValue):
    """
    Adapter interface to get the replacement content value from a given object
    """


class IRecipientsValue(IAttributeValue):
    """
    Adapter interface to get the recipients value from a given object
    """


class IUserDataDocument(IMetadataDocument):
    """
    User generated data document
    """
    content_en = ValidText(title=u'Text to index', required=False)

    title_en = ValidTextLine(title=u'Title to index', required=False)

    redaction_explanation_en = ValidText(title=u'Text to index', required=False)
    replacement_content_en = ValidText(title=u'Text to index', required=False)

    recipients = IndexedIterable(title=u'The recipient entities',
                                 required=False,
                                 value_type=ValidTextLine(title=u"The entiy"),
                                 min_length=0)

    channel = ValidTextLine(title=u'channel value', required=False)

    tags = IndexedIterable(title=u'The tags',
                           required=False,
                           value_type=ValidTextLine(title=u"The tag"),
                           min_length=0)

    keywords_en = IndexedIterable(title=u'The keywords',
                                  required=False,
                                  value_type=ValidTextLine(title=u"The keyword"),
                                  min_length=0)

tagField(IUserDataDocument['channel'], False, IChannelValue)

tagField(IUserDataDocument['recipients'], True, IRecipientsValue)

tagField(IUserDataDocument['tags'], True, ITagsValue, True,
         provided=ITextField)

tagField(IUserDataDocument['title_en'], True, ITitleValue, provided=ITextField)

tagField(IUserDataDocument['content_en'], True,
         IContentValue, provided=(ITextField, ISuggestField))

tagField(IUserDataDocument['redaction_explanation_en'],
         True, IExplanationValue, provided=ITextField)

tagField(IUserDataDocument['replacement_content_en'],
         True, IReplacementContentValue, provided=ITextField)

tagField(IUserDataDocument['keywords_en'], False,
         IKeywordsValue, True, 'text_lower', provided=ITextField)
