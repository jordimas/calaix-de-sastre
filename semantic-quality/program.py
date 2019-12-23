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



def _parse_accents(string):
    string = string.replace(u"í", u'í')
    string = string.replace(u"á", u'á')
    string = string.replace(u"é", u'é')
    string = string.replace(u"ó", u'ó')
    string = string.replace(u"ú", u'ú')
    string = string.replace(u"ñ", u'ñ')
    return string


def read_parameters():
    parser = OptionParser()

    parser.add_option(
        "-s",
        "--source",
        action="store",
        type="string",
        dest="source_file",
        default="",
        help="Source file in Catalan")

    parser.add_option(
        "-k",
        "--key",
        action="store",
        type="string",
        dest="key",
        default="",
        help="Yandex API Key for the their translation service")


    (options, args) = parser.parse_args()

    if len(options.source_file) == 0 or len(options.key) == 0:
        print("Missing parameters)")
        exit(1)        

    return options.source_file, options.key


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

def translate_text_yandex(text, _key):

    SERVER = "https://translate.yandex.net/api/v1.5/tr.json"
    language_pair = 'en-ca'
    url = "{0}/translate?lang={1}&format=plain&key={2}".format(SERVER, language_pair, _key)
    url += "&text=" + urllib.parse.quote_plus(text.encode('utf-8'))
    response = urllib.request.urlopen(url)
    r = response.read().decode("utf-8")
    data = json.loads(r)
    all_text = ''

    texts = data['text']
    for text in texts:
        all_text += text
    return all_text

          
def main():

    print("Takes a translated PO file and translates using machine translation")
    print("then checks levenshtein distance between our translation and the machine one")
    print("to find potential semantic quality issues")

    source_file, key = read_parameters()
    print("Source file: " + source_file)

    input_po = polib.pofile(source_file)
    cnt = 0
    for entry in input_po:

        if len(entry.msgstr) < 4:
            continue

        cnt = cnt + 1

        translated = translate_text_yandex(entry.msgid, key)
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
