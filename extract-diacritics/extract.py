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

import yaml
import os
import operator

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
    word = word.replace('\)', '')
    word = word.replace('\"', '')
    word = word.replace(';', '')
    word = word.replace(':', '')
    word = word.replace('»', '')
    return word

def _read_diacritics(filename):
    print("_read_diacritics")
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
                chars = ['à', 'è', 'í', 'ò', 'ó', 'ú']
                for char in chars:
                    if char in word:
                        found = True
                        
                if found == False:
                    continue

                word = _get_clean_word(word)

                if word in diacritics:
                    cnt = diacritics[word]        
                else:
                    cnt = 0

                cnt = cnt + 1
                diacritics[word] = cnt

                #print(word)
    return diacritics

def _read_clean_diacritics(filename, diacritics):
    print("_read_clean_diacritics")
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

    return cleaned


def _select_sentences_with_diacritics(filename, diacritics):
    print("_select_sentences_with_diacritics")
    diacritics_sentences = {}
    with open(filename, "r") as source:
        clean = 0
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
    return diacritics_sentences


def split_in_six_files():

    strings = 0
    duplicated = 0

#    filename = "ca_dedup.txt"
    filename = "tgt-train.txt"
#    filename = "tgt-val.txt"

    diacritics = _read_diacritics(filename)
    cleaned = _read_clean_diacritics(filename, diacritics)
   
    selected_diacritics = 0
    sorted_dict = sorted(diacritics.items(), key=operator.itemgetter(1), reverse=True)
    for item in sorted_dict:
        key, value = item
        diacritic_cleaned = _get_clean_diacritic(key)
        if diacritic_cleaned not in cleaned:
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

        selected_diacritics = selected_diacritics + 1
        print(f"{key} - {value} ({value_clean})")

    diacritics_sentences = _select_sentences_with_diacritics(filename, diacritics)
    for diacritic in diacritics_sentences.keys():
        print(diacritic)
        sentences = diacritics_sentences[diacritic]
        for sentence in sentences:
            print(f"   {sentence}")

    diacritics_len = len(diacritics)
    print(f"Diacritics: {diacritics_len}, selected: {selected_diacritics}")
 
#    pduplicated = duplicated * 100 / strings
#    print(f"Strings: {strings}, duplicated {duplicated} ({pduplicated:.2f}%)")
 


def main():
    print("Extracts words from corpus that have diacritics and non-diacritic versions")

    split_in_six_files()

if __name__ == "__main__":
    main()
