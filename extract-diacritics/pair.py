#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import logging
import os
import json
from nltk.tokenize.toktok import ToktokTokenizer


_toktok = ToktokTokenizer()


class Word(object):

    def __init__(self, word, lema, pos):
        self.word = word
        self.lema = lema
        self.pos = pos
        self.frequency = 0
        self.sentences = []
        self.detected = 0

    # Part of speech tags documentation:
    # https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb
    def _convert_to_readable_pos(pos_code):
        t = pos_code[0]
        if t == 'A':
            return 0 #"Adjectiu"
        elif t == 'C':
            return 1 # "Conjunció"
        elif t == 'V':
            return 2 # "Verb"
        elif t == 'D':
            return 3 # "Determinant"
        elif t == 'N':
            return 4 # "Nom"
        elif t == 'P':
            return 5 # "Pronom"
        elif t == 'R':
            return 6 # "Advervi"
        else:
            return 7 # "Desconegut"

class Pair(object):

    def __init__(self, diacritic, no_diacritic):
        self.diacritic = diacritic
        self.no_diacritic = no_diacritic


def get_words_dictionaries(pairs):
    diacritics = {}
    no_diacritics = {}

    for pair in pairs.values():
        if pair.diacritic.word not in diacritics:
            diacritics[pair.diacritic.word] = 0
            
        if pair.no_diacritic.word not in no_diacritics:
            no_diacritics[pair.no_diacritic.word] = 0

    return diacritics, no_diacritics






