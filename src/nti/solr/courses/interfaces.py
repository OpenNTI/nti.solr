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
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import ISuggestField
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IMetadataDocument


class ICourseCatalogDocument(IMetadataDocument):

    ntiid = ValidTextLine(title=u'Course catalog ntiid', required=False)

    title_en = ValidTextLine(title=u'Title to index', required=False)

    content_en = ValidText(title=u'Text to index', required=False)

    keywords_en = IndexedIterable(title=u'The keywords',
                                  required=False,
                                  value_type=ValidTextLine(title=u"The keyword"),
                                  min_length=0)

    tags = IndexedIterable(title=u'The tags',
                           required=False,
                           value_type=ValidTextLine(title=u"The tag"),
                           min_length=0)


tagField(ICourseCatalogDocument['ntiid'], True, INTIIDValue)

tagField(ICourseCatalogDocument['title_en'], True,
         ITitleValue, provided=ITextField)

tagField(ICourseCatalogDocument['content_en'], True, IContentValue,
         provided=(ITextField, ISuggestField))

tagField(ICourseCatalogDocument['keywords_en'], False,
         IKeywordsValue, True, 'text_lower',
         provided=ITextField)

tagField(ICourseCatalogDocument['tags'], True, ITagsValue, True,
         provided=ITextField)
