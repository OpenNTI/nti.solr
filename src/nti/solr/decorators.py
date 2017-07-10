#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re

from zope import component

from nti.base._compat import text_

from nti.contentfragments.interfaces import IPlainTextContentFragment

from nti.contentsearch.interfaces import ISearchHit
from nti.contentsearch.interfaces import ISearchFragment
from nti.contentsearch.interfaces import ITranscriptSearchHit
from nti.contentsearch.interfaces import IUserGeneratedDataSearchHit

from nti.externalization.interfaces import StandardExternalFields

from nti.externalization.oids import to_external_ntiid_oid

from nti.externalization.singleton import SingletonDecorator

from nti.solr.query import hl_removeEncodedHTML

ID = StandardExternalFields.ID
NTIID = StandardExternalFields.NTIID
CONTAINER_ID = StandardExternalFields.CONTAINER_ID


@component.adapter(ISearchFragment)
class _SearchFragmentDecorator(object):

    __metaclass__ = SingletonDecorator

    @classmethod
    def sanitize(cls, raw, tag='hit'):
        """
        Transform to plain text, and then make sure the items already
        wrapped in `tag` remain wrapped in `tag`.
        """
        # clean raw string and make it unicode
        raw = re.sub(r'\\/', '/', text_(raw))
        # clean anything that may come from a valid <html> tag
        m = re.match(r"(.*)(<html>.*)", raw)
        raw = m.groups()[1] if m else raw
        # Find all matches
        matches = re.findall(r"<%s>(.*?)</%s>" % (tag, tag), raw)
        matches = set(matches or ())
        raw = IPlainTextContentFragment(raw)
        # Loop and retain our wrapped matches
        for match in matches:
            raw = raw.replace(match, '<%s>%s</%s>' % (tag, match, tag))
        return raw.strip()

    def decorateExternalObject(self, original, external):
        hit = original.__parent__
        # trascript hits are plain text
        if      hit is not None \
            and not ITranscriptSearchHit.providedBy(hit) \
            and hl_removeEncodedHTML(hit.Query):
            for idx, match in enumerate(original.Matches or ()):
                match = self.sanitize(match)
                external['Matches'][idx] = match


@component.adapter(ISearchHit)
class _SearchHitDecorator(object):

    __metaclass__ = SingletonDecorator

    def decorateExternalObject(self, original, external):
        containers = external.get('Containers') or ()
        if CONTAINER_ID not in external and len(containers) == 1:
            external[CONTAINER_ID] = containers[0]
        external.pop(ID, None)


@component.adapter(IUserGeneratedDataSearchHit)
class _UGDSearchHitDecorator(object):

    __metaclass__ = SingletonDecorator

    def decorateExternalObject(self, original, external):
        target = original.Target
        if not external.get(NTIID):
            external[NTIID] = to_external_ntiid_oid(target)
