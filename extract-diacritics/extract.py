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

import os
import json
import operator
import logging

def init_logging():
    logfile = 'extract.log'

    if os.path.isfile(logfile):
        os.remove(logfile)


    logging.basicConfig(filename=logfile, level=logging.DEBUG,
                        format='%(message)s')
                        #format='%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger('')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def _clean_localized(result):
    original = result
    mapping = {
                '’' : '\'',
                'à' : 'à',
                'í' : 'í',
                'ó' : 'ó',
                'è' : 'è',
                'ò' : 'ò',
                'ú' : 'ú',
              }

    for char in mapping.keys():
        result = result.replace(char, mapping[char])

    cleaned = original != result
    return result, cleaned


def _get_clean_diacritic(diacritic):
    diacritic = diacritic.replace('à', 'a')
    diacritic = diacritic.replace('é', 'e')
    diacritic = diacritic.replace('è', 'e')
    diacritic = diacritic.replace('í', 'i')
    diacritic = diacritic.replace('ò', 'o')
    diacritic = diacritic.replace('ó', 'o')
    diacritic = diacritic.replace('ú', 'u')
    return diacritic

def _get_clean_word(word):
    word = word.lower()
    word = word.replace('.', '')
    word = word.replace('s\'', '')
    word = word.replace('d\'', '')
    word = word.replace(',', '')
    word = word.replace('l\'', '')
    word = word.replace(')', '')
    word = word.replace('(', '')
    word = word.replace('\"', '')
    word = word.replace(';', '')
    word = word.replace(':', '')
    word = word.replace('»', '')
    return word

'''
    Select words that have diacritics
    Returns a dictionary with word, frequency

'''
def _read_diacritics(filename):
    print("_read_diacritics")
    logging.debug("_read_diacritics")
    diacritics = {}

    with open(filename, "r") as source:
        clean = 0
        while True:

            src = source.readline().lower()

            if not src:
                break
        
            words = src.split()
            for word in words:
                found = False
                chars = ['à', 'è', 'é', 'í', 'ò', 'ó', 'ú']
                for char in chars:
                    if char in word:
                        found = True
                        
                if found == False:
                    continue

                word = _get_clean_word(word)

#                if len(word) < 4:
#                    logging.debug(f"Skip {word}")
#                    continue
                
                if word in diacritics:
                    cnt = diacritics[word]        
                else:
                    cnt = 0

                cnt = cnt + 1
                diacritics[word] = cnt

                #print(word)


    for diacritic in diacritics:
        logging.debug(f"  {diacritic}")
    return diacritics


'''
    Select words that have clean diacritics that appear in text
    Returns a dictionary with word, frequency
'''
def _read_clean_diacritics(filename, diacritics):
    print("_read_clean_diacritics")
    logging.debug("_read_clean_diacritics")

    cleaned = {}
    for diacritic in diacritics.keys():
        diacritic_cleaned = _get_clean_diacritic(diacritic)
        cleaned[diacritic_cleaned] = 0

    with open(filename, "r") as source:
        while True:

            src = source.readline().lower()

            if not src:
                break
        
            words = src.split()
            for word in words:

                word = _get_clean_word(word)
                if word in cleaned:
                    cnt = cleaned[word]        
                else:
                    cnt = 0

                cnt = cnt + 1
                cleaned[word] = cnt

    for diacritic in cleaned:
        logging.debug(f"  {diacritic}")
    return cleaned

'''
    Returns a dictionary with word, sentences
'''
def _select_sentences_with_diacritics(filename, diacritics):
    print("_select_sentences_with_diacritics")
    logging.debug("_select_sentences_with_diacritics")

    diacritics_sentences = {}
    with open(filename, "r") as source:
        while True:
            src = source.readline().lower()

            if not src:
                break
        
            words = src.split()
            for word in words:
                word = _get_clean_word(word)

                if word not in diacritics:
                    continue

                if word in diacritics_sentences:
                    sentences = diacritics_sentences[word]
                else:
                    sentences = []

                sentences.append(src)
                diacritics_sentences[word] = sentences

                #print(word)

    for diacritic in diacritics_sentences.keys():
        sentences = diacritics_sentences[diacritic]
        logging.debug(f"{diacritic}")
        #for sentence in sentences:
        #    logging.debug(f"  {sentence}")
            

    return diacritics_sentences

command = 'curl --data "language=ca-ES"  --data-urlencode "text@{0}" {1} > "{2}" 2>/dev/null'
server = 'http://172.17.0.2:7001/v2/check'

def run_lt(sentence):

    txt_file = 'lt-txt'
    json_file = 'lt.json'
    with open(txt_file, "w") as writer:
        writer.write(sentence)

    cmd = command.format(txt_file, server, json_file)
#    print(cmd)
    os.system(cmd)

    with open(json_file) as f:
        data = json.load(f)
        matches = data['matches']
        return len(matches)

def _remove_diacritic_sentence(sentence, diacritic):
    clean = _get_clean_diacritic(diacritic)
    return sentence.replace(diacritic, clean)


def split_in_six_files():

#    filename = "ca_dedup.txt"
    filename = "tgt-train.txt"
#    filename = "tgt-val.txt"

    filename = "200000.txt"

    diacritics = _read_diacritics(filename)
    cleaned = _read_clean_diacritics(filename, diacritics)

    selected_diacritics = 0
    sorted_diacritics = sorted(diacritics.items(), key=operator.itemgetter(1), reverse=True)
    sel_diacritics = []

    cleaned_diacritics_sentences = _select_sentences_with_diacritics(filename, cleaned)

    logging.debug("_select diacritics")
    for item in sorted_diacritics:
        key, value = item
        diacritic_cleaned = _get_clean_diacritic(key)
        if diacritic_cleaned not in cleaned:
            continue

        if diacritic_cleaned not in cleaned_diacritics_sentences:
            #logging.debug(f" {diacritic_cleaned} not found")
            continue

#        print(diacritic_cleaned)
#        print(cleaned[diacritic_cleaned])
        value_clean = cleaned[diacritic_cleaned]
        if value_clean == 0:
            continue

        _max = value_clean * 1.50
        _min = value_clean * 0.50

        if value < _min or value > _max:
            continue

        sel_diacritics.append(key)
        selected_diacritics = selected_diacritics + 1
        print(f"{key} - {value} ({value_clean})")

        if selected_diacritics > 100:
            break

    diacritics_sentences = _select_sentences_with_diacritics(filename, diacritics)
#    sorted_diacritics_sentences = sorted(diacritics_sentences.items(), key=operator.itemgetter(1), reverse=True)
    print("_final list")
    for diacritic in sel_diacritics:
        sentences = diacritics_sentences[diacritic]
#        print("*" + diacritic)

        same_errors = 0
        if len(sentences) < 2:
            continue

        for sentence in sentences:
#            print(f"   {sentence}")
            errors_diac = run_lt(sentence)
            sentence_nodiac = _remove_diacritic_sentence(sentence, diacritic)
            errors_nodiac = run_lt(sentence_nodiac)
#            logging.debug(f"{sentence} - {errors_diac}")
#            logging.debug(f"{sentence_nodiac} - {errors_diac}")
            if errors_diac == errors_nodiac:
                same_errors = same_errors + 1

#            print(f"{errors_diac} - {errors_nodiac}")
#            print(sentence)
#            print(errors_diacritics)
#            print(sentence_nodiac)

        logging.debug(f"Same errors? - {diacritic} - {same_errors} - {len(sentences)}")
        if same_errors == len(sentences):
            print("*" + diacritic)
            for sentence in sentences:
                print("   " + sentence)

    diacritics_len = len(diacritics)
    print(f"Diacritics: {diacritics_len}, selected: {selected_diacritics}")
 
#    pduplicated = duplicated * 100 / strings
#    print(f"Strings: {strings}, duplicated {duplicated} ({pduplicated:.2f}%)")
 


def main():
    print("Extracts words from corpus that have diacritics and non-diacritic versions")

    init_logging()
    split_in_six_files()

if __name__ == "__main__":
    main()
