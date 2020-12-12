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

class Word(object):

    def __init__(self, word, lema, pos):
        self.word = word
        self.lema = lema
        self.pos = pos

class Pair(object):

    def __init__(self, diacritic, no_diacritic):
        self.diacritic = diacritic
        self.no_diacritic = no_diacritic

def init_logging():
    logfile = 'data.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG,
                        format='%(message)s')

    logger = logging.getLogger('')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

# Part of speech tags documentation:
# https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-ca/#part-of-speech-verb

def _convert_to_readable_pos(pos_code):
    t = pos_code[0]
    if t == 'A':
        return "Adjectiu"
    elif t == 'C':
        return "Conjunció"
    elif t == 'V':
        return "Verb"
    elif t == 'D':
        return "Determinant"
    elif t == 'N':
        return "Nom"
    elif t == 'P':
        return "Pronom"
    elif t == 'R':
        return "Advervi"
    else:
        return "Desconegut"


def load_dictionary():

    input_file = 'diccionari.txt'
    words = list()
    WORD = 0
    LEMA = 1
    POS = 2
    with open(input_file) as f:
        while True:
            line = f.readline()
            if not line:
                break

            components = line.split()
            _word = components[WORD].lower()
            lema =  components[LEMA].lower()
            pos = _convert_to_readable_pos(components[POS])
            word = Word(_word, lema, pos)
        
            words.append(word)

    logging.debug(f"Words load from dictionary {len(words)}")
    return words

def _get_clean_diacritic(diacritic):
    diacritic = diacritic.replace('à', 'a')
    diacritic = diacritic.replace('é', 'e')
    diacritic = diacritic.replace('è', 'e')
    diacritic = diacritic.replace('í', 'i')
    diacritic = diacritic.replace('ò', 'o')
    diacritic = diacritic.replace('ó', 'o')
    diacritic = diacritic.replace('ú', 'u')
    return diacritic

def words_with_and_without_diacritics(dictionary):
    words = {}
    pairs = []
    for word in dictionary:
        words[word.word] = word

    for word in dictionary:
        no_diatricic_word = _get_clean_diacritic(word.word)
        if no_diatricic_word == word.word:
            continue

        if no_diatricic_word not in words:
            continue

        no_diacritic = words[no_diatricic_word]

        pair = Pair(word, no_diacritic)
#        print(f"{word.word} - {word.pos}, {no_diacritic.word} - {no_diacritic.pos}")
        pairs.append(pair)

    return pairs


def main():
    print("Generates diacritic data from dictionary.")

    init_logging()
    dictionary = load_dictionary()
    pairs = words_with_and_without_diacritics(dictionary)

    with open('diacritics.csv', 'w') as writer:
        for pair in pairs:
            diacritic = pair.diacritic
            no_diacritic = pair.no_diacritic

            writer.write(f"{diacritic.word}\t{diacritic.pos}\t{no_diacritic.word}\t{no_diacritic.pos}\n")

    print(f"Total words: {len(dictionary)}, diacritic/no diacritic {len(pairs)}")
#    for word in dictionary:
#        print(f"{word.word} - {word.lema} {word.pos}")

if __name__ == "__main__":
    main()
