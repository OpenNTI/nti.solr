#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$

 Copyright 2011, Paul McGuire

 implementation of Lucene grammar, as decribed
 at http://svn.apache.org/viewvc/lucene/dev/trunk/lucene/docs/queryparsersyntax.html

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from pyparsing import Group
from pyparsing import Regex
from pyparsing import Literal
from pyparsing import Forward
from pyparsing import Suppress
from pyparsing import Optional
from pyparsing import QuotedString
from pyparsing import ParserElement
from pyparsing import CaselessKeyword

from pyparsing import opAssoc
from pyparsing import infixNotation
from pyparsing import pyparsing_common

ParserElement.enablePackrat()

COLON, LBRACK, RBRACK, LBRACE, RBRACE, TILDE, CARAT = map(Literal, ":[]{}~^")
LPAR, RPAR = map(Suppress, "()")

and_, or_, not_, to_ = map(CaselessKeyword, "AND OR NOT TO".split())
keyword = and_ | or_ | not_ | to_

expression = Forward()

valid_word = Regex(r'([a-zA-Z0-9*_+.-]|\\[!(){}\[\]^"~*?\\:])+').setName("word")
valid_word.setParseAction(
    lambda t : t[0].replace('\\\\', chr(127)).replace('\\', '').replace(chr(127), '\\')
)

q_string = QuotedString('"')
required_modifier = Literal("+")("required")
prohibit_modifier = Literal("-")("prohibit")

integer = Regex(r"\d+").setParseAction(lambda t:int(t[0]))
proximity_modifier = Group(TILDE + integer("proximity"))
number = pyparsing_common.fnumber()
fuzzy_modifier = TILDE + Optional(number, default=0.5)("fuzzy")

term = Forward()
field_name = valid_word().setName("fieldname")
incl_range_search = Group(LBRACK + term("lower") + to_ + term("upper") + RBRACK)
excl_range_search = Group(LBRACE + term("lower") + to_ + term("upper") + RBRACE)
range_search = incl_range_search("incl_range") | excl_range_search("excl_range")
boost = (CARAT + number("boost"))

string_expr = Group(q_string + proximity_modifier) | q_string
word_expr = Group(valid_word + fuzzy_modifier) | valid_word
term << ( Optional(field_name("field") + COLON) +
          (word_expr | string_expr | range_search | Group(LPAR + expression + RPAR)) +
          Optional(boost))
term.setParseAction(lambda t:[t] if 'field' in t or 'boost' in t else None)

expression << infixNotation(term,
    [
        (required_modifier | prohibit_modifier, 1, opAssoc.RIGHT),
        ((not_ | '!').setParseAction(lambda: "NOT"), 1, opAssoc.RIGHT),
        ((and_ | '&&').setParseAction(lambda: "AND"), 2, opAssoc.LEFT),
        (Optional(or_ | '||').setParseAction(lambda: "OR"), 2, opAssoc.LEFT),
    ])
