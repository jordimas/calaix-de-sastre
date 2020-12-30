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
import sys
import os
import fnmatch

def read_file(filename):
    d = {}
    with open(filename) as f:
        lines = f.readlines()

    for line in lines:
        words = line.split(",")
        src = words[0].strip()
        tgt = words[1].strip()
        d[src] = tgt

        src_upper = src[0].upper() + src[1:]
        tgt_upper = tgt[0].upper() + tgt[1:]
        d[src_upper] = tgt_upper

    return d
        

def main():

    print("Canvia per + infinitus")

    changes = 0
    filename = '/home/jordi/sc/calaix-de-sastre/pera/pera.txt'
    replaces = read_file(filename)
    source_filename = sys.argv[1]

    source_po = polib.pofile(source_filename, wrapwidth = 79)
    for entry in source_po:
        msg = entry.msgstr
        for replace in replaces.keys():
            org = msg
            msg = org.replace(replace, replaces[replace])
            if msg != org:
                changes = changes + 1

        entry.msgstr = msg

    source_po.save(sys.argv[1])
    print(f"Changes {changes}")

if __name__ == "__main__":
    main()
