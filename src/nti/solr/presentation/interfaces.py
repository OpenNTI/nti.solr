#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.schema.field import Number
from nti.schema.field import IndexedIterable
from nti.schema.field import Text as ValidText
from nti.schema.field import DecodingValidTextLine as ValidTextLine

from nti.solr.interfaces import tagField
from nti.solr.interfaces import ITextField
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IStringValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import ISuggestField
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IAttributeValue
from nti.solr.interfaces import IMetadataDocument


class IMediaNTIIDValue(IAttributeValue):
    """
    Adapter interface to get the media (video/audio) NTIID associated with a transcript object
    """


class ITranscriptCueStartTimeValue(IAttributeValue):
    """
    Adapter interface to get the transcript cue start time
    """


class ITranscriptCueEndTimeValue(IAttributeValue):
    """
    Adapter interface to get the transcript cue end time
    """


class ITranscriptSourceValue(IAttributeValue):
    """
    Adapter interface to get a file source from a transcript
    """


class ITranscriptDocument(IMetadataDocument):

    media = ValidText(title=u'The media ntiid', required=False)

    content_en = ValidText(title=u'Text to index', required=False)

    cue_end_time = Number(title=u'Cue end time', required=False)
    cue_start_time = Number(title=u'Cue start time', required=False)


tagField(ITranscriptDocument['media'], True, IMediaNTIIDValue)

tagField(ITranscriptDocument['cue_end_time'],
         False, ITranscriptCueStartTimeValue)

tagField(ITranscriptDocument['cue_start_time'],
         False, ITranscriptCueStartTimeValue)

tagField(ITranscriptDocument['content_en'], True,
         IContentValue, provided=(ITextField, ISuggestField))


class ITargetValue(IStringValue):
    """
    Adapter interface to get the target value from a given object
    """


class IAssetDocument(IMetadataDocument):

    ntiid = ValidTextLine(title=u'Asset ntiid', required=False)

    target = ValidTextLine(title=u'Asset target ntiid', required=False)

    title_en = ValidTextLine(title=u'Title to index', required=False)

    content_en = ValidText(title=u'Text to index', required=False)

    keywords_en = IndexedIterable(title=u'The keywords',
                                  required=False,
                                  value_type=ValidTextLine(
                                      title=u"The keyword"),
                                  min_length=0)


tagField(IAssetDocument['ntiid'], True, INTIIDValue)

tagField(IAssetDocument['target'], True, ITargetValue)

tagField(IAssetDocument['title_en'], True, ITitleValue, provided=ITextField)

tagField(IAssetDocument['content_en'], True,
         IContentValue, provided=(ITextField, ISuggestField))

tagField(IAssetDocument['keywords_en'], False,
         IKeywordsValue, True, 'text_lower', provided=ITextField)
