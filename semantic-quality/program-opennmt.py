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
import polib
import urllib
from urllib.parse import urlparse
import urllib.request
import json
import re
import numpy as np
from optparse import OptionParser
import urllib.request, urllib.parse, urllib.error
import time
import os
from shutil import copyfile

def _load_po_into_dictionary(filename):
    strings = {}
    input_po = polib.pofile(filename)

    for entry in input_po:
        strings[entry.msgid] = _parse_accents(entry.msgstr)

    return strings

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
        help="Source file in Catalan (not or partially translated)")

    (options, args) = parser.parse_args()

    if len(options.source_file) == 0:
        print("Missing input file")
        exit(1)

    if options.source_file[-3:] != ".po":
        print("Input file needs to be a PO file")
        exit(1)

    return options.source_file

words = None


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

def create_new_translated_po(source_file):

    target_file = source_file[:-3] + "-new-translation.po"

    print(target_file)    
    copyfile(source_file, target_file)

    input_po = polib.pofile(target_file)
    for entry in input_po:
        entry.msgstr = ''
        entry.flags = 0

    input_po.save()
    directory = os.path.dirname(source_file)
    filename = os.path.basename(target_file)
    command_line=f"-f {filename}"

    command = f"docker run -it -v {directory}:/srv/files/ --env FILE_TYPE='po' --env COMMAND_LINE='{command_line}' --rm jordimash/use-models-tools --name jordimash/use-models-tools"
#    print(command)
    os.system(command)
   

def main():

    print("Takes a translated PO Catalan file, translates it again using machine translation"
          "into Catalan then checks levenshtein distance between our translation and the"
          "machine's one to find potential semantic quality issues\n")

    source_file = read_parameters()
    source_file = os.path.abspath(source_file)
    print("Source file: " + source_file)

    create_new_translated_po(source_file)
    target_file = source_file[:-3] + "-new-translation.po-ca.po"
    opennmt_translations = _load_po_into_dictionary(target_file)

    input_po = polib.pofile(source_file)
    total_strings = 0
    review_strings = 0
    for entry in input_po:

        msgid = entry.msgid
        msgstr = entry.msgstr

        total_strings = total_strings + 1
      
        if len(msgstr.split()) < 8:
            continue

        if 'fuzzy' in entry.flags:
            continue

        if entry.obsolete:
            continue

        if '%' in msgid:
            continue


        translated = opennmt_translations[msgid]
        leven = levenshtein(msgstr, translated)
    
        proportional = leven / len(msgstr)

        if proportional < 0.75:
            continue

        review_strings = review_strings + 1
        print("----")
        print(" {0}".format(msgid))
        print(" {0}".format(msgstr))
        print(" {0}".format(translated))
        print(" {0} ({1})".format(leven, proportional))

    reviewed = total_strings / review_strings if review_strings > 0 else  0
    print("Processed strings:" + str(total_strings))
    print("Strings to review: {:.2f}% ({})".format(reviewed, review_strings))

if __name__ == "__main__":
    main()
