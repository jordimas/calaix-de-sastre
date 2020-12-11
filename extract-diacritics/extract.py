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
from nltk.tokenize.toktok import ToktokTokenizer

def init_logging():
    logfile = 'extract.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG,
                        format='%(message)s')

    logger = logging.getLogger('')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)

_toktok = ToktokTokenizer()

def _get_tokenized_sentence(sentence):
    return _toktok.tokenize(sentence)        


def _get_clean_diacritic(diacritic):
    diacritic = diacritic.replace('à', 'a')
    diacritic = diacritic.replace('é', 'e')
    diacritic = diacritic.replace('è', 'e')
    diacritic = diacritic.replace('í', 'i')
    diacritic = diacritic.replace('ò', 'o')
    diacritic = diacritic.replace('ó', 'o')
    diacritic = diacritic.replace('ú', 'u')
    return diacritic

'''
    Select words that have diacritics
    Returns a dictionary with word, frequency

'''
def _read_diacritics(filename, dictionary):
    logging.info("_read_diacritics")
    diacritics = {}

    with open(filename, "r") as source:
        clean = 0
        while True:

            src = source.readline().lower()

            if not src:
                break
        
            words = _get_tokenized_sentence(src)
            for word in words:
                found = False
                chars = ['à', 'è', 'é', 'í', 'ò', 'ó', 'ú']
                for char in chars:
                    if char in word:
                        found = True
                        
                if found == False:
                    continue

                if word not in dictionary:
                    logging.debug(f"Word not in dictionary {word}")
                    continue

                if word in diacritics:
                    cnt = diacritics[word]
                else:
                    cnt = 0

                cnt = cnt + 1
                diacritics[word] = cnt

    for diacritic in diacritics:
        logging.debug(f"  {diacritic}")

    return diacritics


'''
    Select words that have clean diacritics that appear in text
    Returns a dictionary with word, frequency
'''
def _read_clean_diacritics(filename, diacritics):
    logging.info("_read_clean_diacritics")

    cleaned = {}
    for diacritic in diacritics.keys():
        diacritic_cleaned = _get_clean_diacritic(diacritic)
        cleaned[diacritic_cleaned] = 0

    with open(filename, "r") as source:
        while True:

            src = source.readline().lower()

            if not src:
                break
        
            words = _get_tokenized_sentence(src)
            for word in words:

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
    logging.info("_select_sentences_with_diacritics")

    diacritics_sentences = {}
    with open(filename, "r") as source:
        while True:
            src = source.readline().lower()

            if not src:
                break
        
            words = _get_tokenized_sentence(src)
            for word in words:
                if word not in diacritics:
                    continue

                if word in diacritics_sentences:
                    sentences = diacritics_sentences[word]
                else:
                    sentences = []

                if len(sentences) < 10:
                    sentences.append(src)
                    diacritics_sentences[word] = sentences

    for diacritic in diacritics_sentences.keys():
        sentences = diacritics_sentences[diacritic]
        logging.debug(f"{diacritic}")
        #for sentence in sentences:
        #    logging.debug(f"  {sentence}")
            

    return diacritics_sentences

command = 'curl --data "language=ca-ES"  --data-urlencode "text@{0}" {1} > "{2}" 2>/dev/null'
server = 'http://172.17.0.2:7001/v2/check'

def run_lt(filename):
    matches = 0

    try:
        #filename = filename.replace("/", "_")
        txt_file = filename + ".txt"
        json_file = filename + ".json"

        cmd = command.format(txt_file, server, json_file)
        os.system(cmd)

        with open(json_file) as f:
            data = json.load(f)
            matches = data['matches']
            matches = len(matches)

        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4, separators=(',', ': '))
    
    except Exception as e:
        logging.error(e)

    return matches
def _remove_diacritic_sentence(sentence, diacritic):
    clean = _get_clean_diacritic(diacritic)
    return sentence.replace(diacritic, clean)


def _get_selected_diacritics(filename, cleaned, diacritics):
    sel_diacritics = []
    selected_diacritics = 0

    cleaned_diacritics_sentences = _select_sentences_with_diacritics(filename, cleaned)
    sorted_diacritics = sorted(diacritics.items(), key=operator.itemgetter(1), reverse=True)

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
        if value < 2 or value_clean < 2:
            continue

#        _max = value_clean * 1.50
#        _min = value_clean * 0.50

#        if value < _min or value > _max:
#            continue

        sel_diacritics.append(key)
        selected_diacritics = selected_diacritics + 1
        logging.debug(f"{key} - {value} ({value_clean})")

#        if selected_diacritics > 100:
#            break

    diacritics_len = len(diacritics)
    print(f"Diacritics: {diacritics_len}, selected: {selected_diacritics}")
    return sel_diacritics


def _write_debug_files(filename_diacritics, filename_nodiacritics, diacritic, sentences):

    try:
        with open(filename_diacritics + ".txt", "w") as diac_writer, \
             open(filename_nodiacritics  + ".txt", "w") as nodiac_writer:
            for sentence in sentences[:5]:
                sentence_nodiac = _remove_diacritic_sentence(sentence, diacritic)
                nodiac_writer.write(sentence_nodiac + "\n")
                diac_writer.write(sentence + "\n")

    except Exception as e:
        logging.error(e)

def process_corpus(dictionary):

#    filename = "ca_dedup.txt"
#    filename = "tgt-train.txt"
#    filename = "tgt-val.txt"
    filename = "500000.txt"

    diacritics = _read_diacritics(filename, dictionary)
    cleaned = _read_clean_diacritics(filename, diacritics)

    sel_diacritics = _get_selected_diacritics(filename, cleaned, diacritics)
    diacritics_sentences = _select_sentences_with_diacritics(filename, diacritics)
  
    logging.info("_final list")
    cnt = 0
    for diacritic in sel_diacritics:
        sentences = diacritics_sentences[diacritic]
        logging.debug(f"{diacritic} - pos: {cnt} sentences: {len(sentences)}")

        same_errors = 0
        cnt = cnt + 1
#        if len(sentences) < 2:
#            continue

#        if len(diacritic) < 4:
#            continue

        name = _get_clean_diacritic(diacritic)
        filename_diacritics = f'data/{name}_dia'
        filename_nodiacritics = f'data/{name}_nodia'

        _write_debug_files(filename_diacritics, filename_nodiacritics, diacritic, sentences)

        errors_diac = run_lt(filename_diacritics)
        errors_nodiac = run_lt(filename_nodiacritics)
 
        logging.debug(f"Same errors? - {diacritic} - {errors_diac} - {errors_nodiac}")
        if errors_diac == errors_nodiac:
            clean_diacritic =  _get_clean_diacritic(diacritic)
            print(f"*** {diacritic} {diacritics[diacritic]} - {cleaned[clean_diacritic]}")
            for sentence in sentences:
                print("   " + sentence)

def load_dictionary():

    input_file = 'diccionari.txt'
    words = set()
    with open(input_file) as f:
        while True:
            line = f.readline()
            if not line:
                break

            word = line.split()[0].lower()
            if word not in words:
                words.add(word)

    logging.debug(f"Words load from dictionary {len(words)}")
    return words

def main():
    print("Extracts words from corpus that have diacritics and non-diacritic versions")

    init_logging()
    dictionary = load_dictionary()
    process_corpus(dictionary)

if __name__ == "__main__":
    main()
