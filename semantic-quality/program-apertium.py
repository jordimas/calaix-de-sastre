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

def _get_marker(pos, end, self_closed):
    if self_closed:
        return "MATCHSELF-" + str(pos)

    s = ''
    if end is True:
        s = "END"
    return s + "MATCH-" + str(pos)

def _get_translation(text):

    # Request translation
    url = "https://www.softcatala.org/apertium/json/translate?langpair=es|ca&markUnknown=no"
    url += "&q=" + urllib.parse.quote_plus(text.encode('utf-8'))
    #print("url->" + url)

    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    translated =  data['responseData']['translatedText']
    #print("Translated (returned):" + translated)
    return translated

tm = None

def _load_tm(filename):
    strings = {}
    input_po = polib.pofile(filename)

    for entry in input_po:
        if entry.msgstr is '':
            continue

        strings[entry.msgid] = entry.msgstr

    print("Read Translation memory:" + str(len(strings)))
    return strings

def _create_markers_in_string(text):
    markers = {}
    regex = re.compile(r"\<(.*?)\>", re.VERBOSE)
    matches = regex.findall(text)
    pos = 0
    for match in matches:
        match = '<' + match + '>'
        where = text.find(match)
        end = match[1] == '/'
        self_closed = match[len(match) - 2] == '/'
        marker = _get_marker(pos, end, self_closed)

        if where + len(match) < len(text):
            marker = marker + ' '

        if where > 0:
            marker = ' ' + marker
        
        text = text.replace(match, marker, 1)
        markers[marker] = match
        pos = pos + 1

    return markers, text

def _translate_from_spanish(english, text):

    global tm

    if tm is None:
        tm = _load_tm('tm/gimp-tm.po')
        print("memory loaded")

    # Create markers for HTML tags Spanish
    markers, text = _create_markers_in_string(text)

    # Create markers for HTML tags English
    markers_en, text_en = _create_markers_in_string(english)

    # Create markers for HTML text
    markers_text = {}
    regex = re.compile(r"MATCH-[0-9](.*?)ENDMATCH-[0-9]", re.VERBOSE)
    matches = regex.findall(text)
    matches_en = regex.findall(text_en)
    
    pos = 0
    ca_pos = 0
    if len(markers_en) == len(markers):
        for match in matches:
            eng = matches_en[pos].strip()
            if eng in tm:
                #print("Found text in tags in TM:'" + eng.encode("utf-8") + "'")
                marker = "CATEXT-" + str(ca_pos)
                #print("Marker: '{0}'".format(marker.encode("utf-8")))
                #print("Match: '{0}'".format(match.encode("utf-8")))
                text = text.replace(match.strip(), marker, 1)
                markers_text[marker] = tm[eng]
                ca_pos = ca_pos + 1

            pos = pos + 1
    else:
        print("Different number of matches: {0} {1} for {2}. Cannot look for word between tags in TM".format(len(markers_en), len(markers), english))

    translated = _get_translation(text)

    # Put back markers for HTML tags Spanish
    for marker in markers.keys():
        translated = translated.replace(marker, markers[marker], 1)
    
    # Put back markers for HTML text
    for marker in markers_text.keys():
        translated = translated.replace(marker, markers_text[marker], 1)

    #print("Translated:" + str(translated))
    return translated

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


def search_for_tm(entry):
    reported = []
    for eng in tm:
        eng_lo = eng.lower()
        if eng_lo not in reported and len(eng_lo) > 5 and eng_lo in entry.msgid.lower():
            value = tm[eng]
            if value.lower() not in entry.msgstr.lower():
                entry.tcomment += u"\n {0} -> {1}".format(eng, unicode(tm[eng]))
                reported.append(eng)

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

def main():

    print("Takes a translated PO Catalan file, then a Spanish file that translates using machine translation into Catalan")
    print("then checks levenshtein distance between our translation and the machine's one")
    print("to find potential semantic quality issues")

    source_file, translated_file = read_parameters()
    print("Source file: " + source_file)
    print("Translated file: " + translated_file)

    # Create a dictionary with translated segments in Spanish
    strings = _load_po_into_dictionary(translated_file)

    input_po = polib.pofile(source_file)
    cnt = 0
    for entry in input_po:

        if entry.msgid not in strings:
            continue

        if len(entry.msgstr) < 4:
            continue

        cnt = cnt + 1

        sp = _parse_accents(strings[entry.msgid])
        translated = _translate_from_spanish(entry.msgid, sp)
        translated = _word_replacement(translated)

        leven = levenshtein(entry.msgstr, translated)
    
        proportional = leven / len(entry.msgstr)

        if proportional < 0.9:
            continue

        print("----")
        print(" {0}".format(entry.msgid))
        print(" {0}".format(entry.msgstr))
        print(" {0}".format(translated))
        print(" {0} ({1})".format(leven, proportional))

    print("Processed strings:" + str(cnt))

if __name__ == "__main__":
    main()
