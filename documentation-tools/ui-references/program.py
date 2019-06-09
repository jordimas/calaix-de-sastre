#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Jordi Mas i Hernandez <jmas@softcatala.org>
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


import polib
import re

def _load_po_into_dictionary(filename):
    strings = {}
    input_po = polib.pofile(filename)

    for entry in input_po:
        if entry.msgstr is '' or '@@image' in entry.msgid:
            continue

        strings[entry.msgid.lower()] = entry.msgstr

    print("Read Spanish sentences:" + str(len(strings)))
    return strings

def _parse_accents(string):
    string = string.replace(u"í", u'í')
    string = string.replace(u"á", u'á')
    string = string.replace(u"é", u'é')
    string = string.replace(u"ó", u'ó')
    string = string.replace(u"ú", u'ú')
    string = string.replace(u"ñ", u'ñ')
    return string

def _load_tm(filename):
    strings = {}
    input_po = polib.pofile(filename)

    for entry in input_po:
        if entry.msgstr is '':
            continue

        strings[entry.msgid] = entry.msgstr

    print("Read Translation memory:" + str(len(strings)))
    return strings


def extract_text(entry):

    regex = re.compile(r"\<(.*?)\>(.*?)</(.*?)\>", re.VERBOSE)
    matches = regex.findall(entry)
    texts = list()

    for match in matches:
        match = match[1]
        texts.append(match)
        where = entry.find(match)
#        print(entry)
#        print("->" + match)

    return texts

          
def main():

    print("Checks that UI elements in documentation use the same names than in the UI")
    doc_file = '/home/jordi/dev/gedit/gedit-upstream/help/ca/ca.po'
    ui_file = '/home/jordi/dev/gedit/gedit-upstream/po/ca.po'

    ui_strings = _load_po_into_dictionary(ui_file)

    cnt = 0
    input_po = polib.pofile(doc_file)
    for entry in input_po:
        #  <gui>reference</gui>
        srcs = extract_text(entry.msgid)
        trgs = extract_text(entry.msgstr)
        if len(srcs) != len(trgs):
            continue

        for i in range(0, len(srcs)):
            #print(srcs[i])
            #print(trgs[i])
            if srcs[i].lower() not in ui_strings:
                continue

            if len(srcs[i].lower()) < 4:
                continue

            trg_memory = ui_strings[srcs[i].lower()]
            if trg_memory.lower() != trgs[i].lower():
                print("src:" + entry.msgid)
                print("src:" + srcs[i])
                print("trg:" + trgs[i])
                print("trg_memory:" + trg_memory)
                print("--")
                cnt = cnt  +1

    print("Potential errors found:" + str(cnt))

if __name__ == "__main__":
    main()
