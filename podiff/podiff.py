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

def print_entry(entry, filename, firstError):

    print('--')
    print('msgid:' + entry.msgid)
    print('msgstr:' + entry.msgstr)

def main():

    print("Diff two PO files")

    source_entries = {}
    target_entries = {}

    source_filename = '/home/jordi/sc/tmt/tmt/src/fedora-old/fedora-tm.po'
    target_filename = '/home/jordi/sc/tmt/tmt/src/output/fedora-tm.po'

    source_duplicates_same_translation = 0
    source_duplicates_different_translation = 0

    target_duplicates_same_translation = 0
    target_duplicates_different_translation = 0
  
    # Load source strings
    source_po = polib.pofile(source_filename)
    for entry in source_po:
        key = entry.msgid
        if key in source_entries:
            if source_entries[key] == entry.msgid:
                source_duplicates_same_translation += 1 
            else:
                source_duplicates_different_translation += 1
      
        source_entries[key] = entry.msgid

    # Load target strings
    target_po = polib.pofile(target_filename)
    for entry in target_po:
        key = entry.msgid


xx

                target_duplicates_same_translation += 1 
            else:
                target_duplicates_different_translation += 1

        target_entries[key] = entry.msgid

    print('Added strings')x
    added = 0
    for key in target_entries.keys():
        if key not in source_entries:
            print(' {0}'.format(key))
            added = added + 1

    print('Missing strings')
    missing = 0
    for key in source_entries.keys():
        if key not in target_entries:
            print(' {0}'.format(key))
            missing = missing + 1

    print('Added:' + str(added))
    print('Missing:' + str(missing))
    print('Source duplicates with same translation: ' +  str(source_duplicates_same_translation))
    print('Source duplicates with different translation: ' + str(source_duplicates_different_translation))
    print('Target duplicates with same translation: ' +  str(target_duplicates_same_translation))
    print('Target duplicates with different translation: ' + str(target_duplicates_different_translation))

if __name__ == "__main__":
    main()
