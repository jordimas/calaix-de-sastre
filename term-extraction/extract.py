#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import json
import polib
import re
import os
import fnmatch
import logging

def init_logging():
    logfile = 'extract.log'

    if os.path.isfile(logfile):
        os.remove(logfile)

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
#    logger = logging.getLogger('')
#    console = logging.StreamHandler()
#    console.setLevel(logging.INFO)
#    logger.addHandler(console)


def clean_string_src(text):
    text = re.sub('[_&~:.]', '', text)
    text = re.sub('<[^>]*>', '', text) # Remove HTML tags
    return text

def clean_string_trg(text):
    text = clean_string_src(text)
    text = text.replace("l'", "")
    return text

def find_matching_strings(word, sentence, filename, stems):

    matches = []

    source_po = polib.pofile(filename)
    for entry in source_po:
        if entry.fuzzy or entry.obsolete:
            continue

        if len(entry.msgid) > 50:
            continue

        msgid = clean_string_src(entry.msgid)

        words = msgid.split()
        if word not in words:
            continue

        if entry.msgid == sentence:
            continue

        matches.append(entry)
        logging.debug("  word '{0}' matched '{1}' ({2})".format(word, entry.msgid, entry.msgstr))

    return matches

def load_stemming_dict():
    dictionary = 'diccionari.txt'
    stems = {}
    
    with open(dictionary) as f:
        lines = f.readlines()
        for line in lines:
            words = line.split()
            stems[words[0]] = words[1]
#            print("Storing {0} -> {1}".format(words[0], words[1]))

    logging.debug("Dictionary loaded")
    return stems

#
# If the sentence that we are processing is "File not found in floppy"
# We want to make sure that when we evaluate the other strings to extract terminology
# they do not contain  "found" and "floppy" to prevent incorrect matching of the term
# 
def does_setence_contains_a_word_from_list(msgid,#string to evaluate
       en_sentence,# sentence that we are processing
       en_word):# word that we are processing

    # List of words that cannot be contained sentences to extrac terms
    en_words_tmp = en_sentence.lower().split()
#    print("removing '{0}' in '{1}'".format(en_word, en_sentence))
    en_words_tmp.remove(en_word)

    # Remove all the words < 5 (do not qualify)
    en_words = set()
    for word in en_words_tmp:
        if len(word) < 5:
            continue
        en_words.add(word)

    words = msgid.lower().split()
    for word in words:
        if word in en_words:
            return True

    return False


def most_frequent_translation(en_word, en_sentence, entries):

    frequencies = {}
    most_frequency = 0
    most_word = None

    for entry in entries:
        words = entry.msgid.lower().split()

        if does_setence_contains_a_word_from_list(entry.msgid.lower(), en_sentence, en_word):
            continue

        msgstr = clean_string_trg(entry.msgstr)
        words = msgstr.lower().split()
        for word in words:
            if len(word) < 5:
                continue

            if word in frequencies:
                frequency = frequencies[word]
            else:
                frequency = 0

            frequency += 1
            frequencies[word] = frequency

            if frequency > most_frequency:
                most_frequency = frequency
                most_word = word
    
    return most_word

def show_inconsistencies(entries, term):
    for entry in entries:
        words = clean_string_trg(entry.msgstr).lower().split()
        if term in words:
            continue
        s = (" Inconsistency: {0} ({1})".format(entry.msgstr, entry.msgid))
        logging.debug(s)
        print(s)

def main():

    print("Terminology extraction full sentence with steaming")

    init_logging()
    stems = load_stemming_dict()

    processed_words = set()
    filename = 'gnome-tm.po'   
    source_po = polib.pofile(filename)
    for entry in source_po:
        if len(entry.msgid) > 50:
            continue

        words = entry.msgid.lower().split()
        for word in words:
            if word in processed_words:
                continue

            if len(word) < 6:
                continue

            matches = find_matching_strings(word, entry.msgid, filename, stems)
            processed_words.add(word)
            if len(matches) < 5:
                continue

            translation = most_frequent_translation(word, entry.msgid, matches)
            s = ("Recommendation: {0} -> {1} ({2})".format(word, translation, entry.msgid))
            logging.debug(s)
            print(s)

            show_inconsistencies(matches, translation)
            s = ("----")
            logging.debug(s)
            print(s)
  
            
if __name__ == "__main__":
    main()
