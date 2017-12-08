#!/usr/bin/env python2

"""
Read a file of the format:

key1:value1
key2:value2

and save it as a .btree file
"""

from bplustree import SBplusTree
import os
import sys

if len(sys.argv) != 2:
    print("ERROR: To use './btree-build.py FILENAME'" % input_filename)
    sys.exit(1)

input_filename = sys.argv[1]
btree_filename = input_filename + '.btree'

if not os.path.isfile(input_filename):
    print("ERROR: %s does not exist" % input_filename)
    sys.exit(1)

if os.path.isfile(btree_filename):
    print("ERROR: %s already exist" % btree_filename)
    sys.exit(1)

with open(btree_filename, 'w+b') as fh_btree:
    B = SBplusTree(fh_btree, position=0, nodesize=200, keylen=12)
    B.startup()
    count = 0

    with open(input_filename, 'r') as fh:

        for line in fh:
            (key, value) = line.strip().split(':')
            B[key] = value

            count += 1

            if count % 100000 == 0:
                print("Added %d" % count)

    print("btree has %d entries" % len(B))
