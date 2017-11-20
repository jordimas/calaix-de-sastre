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


def find(directory, pattern):
    filelist = []

    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                filelist.append(filename)

    filelist.sort()
    return filelist

def find_dirs(directory, pattern):
    dirlist = []

    for root, dirs, files in os.walk(directory):
        for basename in dirs:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                dirlist.append(filename)

    dirlist.sort()
    return dirlist

def find_recursive(directory, pattern):
    filelist_set = set()
    dirs = find_dirs(directory, "*")
    for _dir in dirs:
        files = find(_dir, pattern)
        for f in files:
            filelist_set.add(f)

    filelist = list(filelist_set)
    filelist.sort()
    return filelist

def print_entry(entry, filename, firstError):

    if firstError is False:
        print('**** Found error:' + filename)

    print('--')
    print('msgid:' + entry.msgid)
    print('msgstr:' + entry.msgstr)

def main():

    print("Looks for missing tags in the GIMP documentation")
    filenames = find_recursive('/home/jordi/dev/gimp-help-2/po/ca/', '*.po')

    errors = 0
    for filename in filenames:
        try:
    
            firstError = False
            input_po = polib.pofile(filename)
            for entry in input_po:
                if len(entry.msgstr) == 0:
                    continue

                ids = re.search('.*(<(.*)>).*', entry.msgid, re.IGNORECASE)
                strs = re.search('.*(<(.*)>).*', entry.msgstr, re.IGNORECASE)

                if not ids and not strs:
                    continue
               
                if ids and not strs:
                    print_entry(entry, filename, firstError)
                    errors = errors + 1
                    firstError = False
                    continue

                if not ids and strs:
                    print_entry(entry, filename, firstError)
                    errors = errors + 1
                    firstError = False
                    continue

                for i in range(len(ids.groups()) - 1):
                    for s in range(len(strs.groups()) - 1):
                        if ids.group(i + 1) != strs.group(i + 1):
                            print_entry(entry, filename, firstError)
                            errors = errors + 1
                            firstError = False
                            continue

        except Exception as e:
            print('Cannot analyze {0} -> {1}'.format(filename, e))
                
    print("Total errors:" + str(errors))

if __name__ == "__main__":
    main()
