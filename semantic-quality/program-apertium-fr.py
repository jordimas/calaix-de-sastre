#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Jordi Mas i Hernandez <jmas@softcatala.org>
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
import polib
import urllib
from urllib.parse import urlparse
import urllib.request
import json
import re
import numpy as np
from optparse import OptionParser
import urllib.request, urllib.parse, urllib.error
import json
import time
import os


def _load_po_into_dictionary(filename):
    strings = {}
    input_po = polib.pofile(filename)

    for entry in input_po:
        if entry.msgstr is '' or '@@image' in entry.msgid:
            continue

        strings[entry.msgid] = _parse_accents(entry.msgstr)

    #print("Read Spanish sentences:" + str(len(strings)))
    return strings

def _parse_accents(string):
    string = string.replace(u"í", u'í')
    string = string.replace(u"á", u'á')
    string = string.replace(u"é", u'é')
    string = string.replace(u"ó", u'ó')
    string = string.replace(u"ú", u'ú')
    string = string.replace(u"ñ", u'ñ')
    return string


def _get_translation(text):

    # Request translation
    #url = "https://www.softcatala.org/apertium/json/translate?langpair=es|ca&markUnknown=no"
    url = "http://localhost:8050/translate?langpair=es|ca&markUnknown=no"
    url += "&q=" + urllib.parse.quote_plus(text.encode('utf-8'))
    #print("url->" + url)

    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        translated =  data['responseData']['translatedText']
        return translated

    except Exception as e:
        print("ERROR: calling _get_translation: " + str(e))
        time.sleep(5)
        return ""


def _translate_from_spanish(english, text):
    with open("input.txt", "w") as text_file:
        text_file.write(text)
        text_file.close()

    cmd = "apertium spa-cat -u input.txt output.txt"
    os.system(cmd)

    with open ("output.txt", "r") as myfile:
        line_list = myfile.readlines()
        translation = ' '.join([str(elem) for elem in line_list]) 
        translation = translation.replace('\n', '')
#        print("text->" + text)
#        print("cmd->" + cmd)
#        print("translation->" + translation)
#        print("translation raw->" + str(line_list))
        return translation



def _translate_from_spanish2(english, text):
    translated = _get_translation(text)
    return translated

def _translate_from_french(english, text):

    with open("input.txt", "w") as text_file:
        text_file.write(text)
        text_file.close()

    cmd = "apertium fra-cat -u input.txt output.txt"
    os.system(cmd)

    with open ("output.txt", "r") as myfile:
        line_list = myfile.readlines()
        translation = ' '.join([str(elem) for elem in line_list]) 
        translation = translation.replace('\n', '')
#        print("text->" + text)
#        print("cmd->" + cmd)
#        print("translation->" + translation)
#        print("translation raw->" + str(line_list))
        return translation
    

def _translate_from_french2(english, text):
    # Request translation
    url = "http://localhost:8050/translate?langpair=fr|ca&markUnknown=no"
    url += "&q=" + urllib.parse.quote_plus(text.encode('utf-8'))
    print("url->" + url)

    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        translated =  data['responseData']['translatedText']
        print("translated->" + translated)
        return translated

    except Exception as e:
        print("ERROR: _translate_from_french: " + str(e))
        time.sleep(5)
        return ""


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-s",
        "--source",
        action="store",
        type="string",
        dest="source_file",
        default="",
        help="Source file in Catalan (not or partially translated)")

    parser.add_option(
        "-t",
        "--translated",
        action="store",
        type="string",
        dest="translated_file",
        default="",
        help="Source file in Spanish (translated)")

    (options, args) = parser.parse_args()

    if len(options.source_file) == 0 or len(options.translated_file) == 0:
        print("Missing inputs file(s)")
        exit(1)

    return (options.source_file, options.translated_file)

words = None

def _word_replacement(string):

    global words

    if words is None:
        words = {}
        with open('word-replace.txt') as f:
            print("Read word-replace.txt")
            lines = f.readlines()
            for line in lines:
                if ',' not in line:
                    continue

                source, target = line.split(',')
                if source is not None and target is not None:
                    source = source.strip()
                    target = target.strip()
                    #words[unicode(source, "utf-8")] = unicode(target, "utf-8")
                    words[source] = target

    for key in words.keys():
        string = string.replace(key, words[key])

    return string

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

def clean_string(text):
    text = re.sub('[_&~]', '', text)
    text = re.sub('<[^>]*>', '', text) # Remove HTML tags
    return text

def main():

    print("Takes a translated PO Catalan file, then a Spanish file that translates using machine translation into Catalan")
    print("then checks levenshtein distance between our translation and the machine's one")
    print("to find potential semantic quality issues")

#   source_file, translated_file = read_parameters()

    source_file = '/home/jordi/sc/tmt/src/output/gimp-tm.po'
    translated_file = '/home/jordi/sc/tmt2/src/output/gimp-tm.po'
    translated_file_fr = '/home/jordi/sc/tmt3/src/output/gimp-tm.po'

    print("Source file: " + source_file)
    print("Translated file: " + translated_file)

    # Create a dictionary with translated segments in Spanish
    strings = _load_po_into_dictionary(translated_file)
    strings_fr = _load_po_into_dictionary(translated_file_fr)

    input_po = polib.pofile(source_file)
    total_strings = 0
    review_strings = 0
    for entry in input_po:

        msgid = entry.msgid
        msgstr = clean_string(entry.msgstr)

        if entry.msgid not in strings:
            continue

        if entry.msgid not in strings_fr:
            continue

        if len(msgstr) < 4:
            continue

        if 'fuzzy' in entry.flags:
            continue

        if entry.obsolete:
            continue

        if len(strings[msgid]) == 0:
            continue

        if len(strings_fr[msgid]) == 0:
            continue

        total_strings = total_strings + 1

        sp = _parse_accents(strings[msgid])
        sp = clean_string(sp)
        translated = _translate_from_spanish(msgid, sp)
        #translated = _word_replacement(translated)

        fr = _parse_accents(strings_fr[msgid])
        fr = clean_string(fr)
        translated_fr = _translate_from_french(msgid, fr)

        leven = levenshtein(msgstr, translated)
        leven_fr = levenshtein(msgstr, translated_fr)
        leven_fr_sp = levenshtein(translated, translated_fr)

        if (len(translated_fr)) == 0:
            continue
    
        proportional = leven / len(msgstr)
        proportional_fr = leven_fr / len(msgstr)
        proportional_fr_sp = leven_fr_sp / len(translated_fr)

        # The lower the closest macht
        if proportional_fr_sp > 0.5 or proportional < 1.0 or proportional_fr < 1.0:
            continue

        review_strings = review_strings + 1
        print("----")
        if entry.msgctxt is not None and len(entry.msgctxt) > 0:
            print(" {0} (msgctxt)".format(entry.msgctxt))

        print(" {0} (en)".format(msgid))
        print(" {0} (ca)".format(msgstr))
        print(" {0} (from sp)".format(translated))
        print(" {0} (from fr)".format(translated_fr))
        print(" {0} ({1}) sp".format(leven, proportional))
        print(" {0} ({1}) fr".format(leven_fr, proportional_fr))
        print(" {0} ({1}) fr-sp".format(leven_fr_sp, proportional_fr_sp))

    reviewed = total_strings / review_strings if review_strings > 0 else  0
    print("Processed strings:" + str(total_strings))
    print("Strings to review: {:.2f}% ({})".format(reviewed, review_strings))

if __name__ == "__main__":
    main()
