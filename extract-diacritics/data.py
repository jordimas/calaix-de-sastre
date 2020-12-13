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
from nltk.tokenize.toktok import ToktokTokenizer

_toktok = ToktokTokenizer()


class Word(object):

    def __init__(self, word, lema, pos):
        self.word = word
        self.lema = lema
        self.pos = pos
        self.frequency = 0

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


def load_dictionary():

    input_file = 'diccionari.txt'
    words = list()
    WORD = 0
    LEMA = 1
    POS = 2

    duplicated = set()
    with open(input_file) as f:
        while True:
            line = f.readline()
            if not line:
                break

            components = line.split()
            _word = components[WORD].lower()

            if _word in duplicated:
                continue
    
            duplicated.add(_word)

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

def get_pairs(dictionary):
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

def get_words_dictionaries(pairs):
    diacritics = {}
    no_diacritics = {}

    for pair in pairs:
        if pair.diacritic.word not in diacritics:
            diacritics[pair.diacritic.word] = 0
            
        if pair.no_diacritic.word not in no_diacritics:
            no_diacritics[pair.no_diacritic.word] = 0

    return diacritics, no_diacritics


def _get_tokenized_sentence(sentence):
    return _toktok.tokenize(sentence)        


def set_dictionaries_frequencies(corpus, diacritics, no_diacritics):
    with open(corpus, "r") as source:
        while True:

            src = source.readline().lower()

            if not src:
                break

            words = _get_tokenized_sentence(src)
            for word in words:
                if word in diacritics:
                    frequency = diacritics[word]
                    diacritics[word] = frequency + 1

                if word in no_diacritics:
                    frequency = no_diacritics[word]
                    no_diacritics[word] = frequency + 1

def update_pairs(pairs, diacritics, no_diacritics):
    for pair in pairs:
        if pair.diacritic.word in diacritics:
            frequency = diacritics[pair.diacritic.word]
            pair.diacritic.frequency = frequency

        if pair.no_diacritic.word in no_diacritics:
            frequency = no_diacritics[pair.no_diacritic.word]
            pair.no_diacritic.frequency = frequency


def main():
    print("Generates diacritic data from dictionary.")

    init_logging()
    dictionary = load_dictionary()
    pairs = get_pairs(dictionary)
    diacritics, no_diacritics = get_words_dictionaries(pairs)

#    set_dictionaries_frequencies("ca_dedup.txt", diacritics, no_diacritics)
    #set_dictionaries_frequencies("tgt-train.txt", diacritics, no_diacritics)
    set_dictionaries_frequencies("200000.txt", diacritics, no_diacritics)
    update_pairs(pairs, diacritics, no_diacritics)

    diacritics_corpus = 0
    position = 0
    not_found_in_corpus_pos = {}
    with open('diacritics.csv', 'w') as writer:
        msg = f"diacritic_word\tdiacritic_pos\tdiacritic_freq\t"
        msg += f"no_diacritic_word\tno_diacritic_pos\tno_diacritic_freq\t"
        msg += f"total_freq\tcnt\n"

        writer.write(msg)
        for pair in pairs:
            diacritic = pair.diacritic
            no_diacritic = pair.no_diacritic

            if diacritic.frequency == 0 and no_diacritic.frequency == 0:
                logging.debug(f"Frequency 0: {diacritic.word}, {diacritic.pos}")
                pos = diacritic.pos
                if pos in not_found_in_corpus_pos:
                    counter = not_found_in_corpus_pos[pos]
                else:
                    counter = 0

                counter = counter + 1
                not_found_in_corpus_pos[pos] = counter
                continue

            total_freq = diacritic.frequency + no_diacritic.frequency

            msg = f"{diacritic.word}\t{diacritic.pos}\t{diacritic.frequency}\t"
            msg += f"{no_diacritic.word}\t{no_diacritic.pos}\t{no_diacritic.frequency}\t{total_freq}\t{position}\n"
            diacritics_corpus = diacritics_corpus + 1
            position = position + 1
            writer.write(msg)

    diacritics_dict = len(pairs)
    pdiacritics_dict = diacritics_dict * 100 / len(dictionary)
    pdiacritics_corpus = diacritics_corpus * 100 / diacritics_dict
    

    logging.info(f"Total unique words in dictionary: {len(dictionary)}")
    logging.info(f"Diacritic/no diacritic {diacritics_dict} ({pdiacritics_dict:.2f}%) (in dictionary)")
    logging.info(f"Diacritic/no diacritic {diacritics_corpus} ({pdiacritics_corpus:.2f}%) (in corpus)")


    len_pos = total = sum(int(v) for v in not_found_in_corpus_pos.values())
    print(len_pos)
    for pos in not_found_in_corpus_pos:
        counter = not_found_in_corpus_pos[pos]
        pcounter = counter * 100 / len_pos
        logging.info(f"Not found in corpus, category {pos} - {counter}  ({pcounter:.2f}%)")
#    for word in dictionary:
#        print(f"{word.word} - {word.lema} {word.pos}")

if __name__ == "__main__":
    main()
