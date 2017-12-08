#!/usr/bin/env python2

"""
Use recopy_sbplus to rebuild a .btree so that it takes less disk space.
"""

from bplustree import recopy_sbplus
import os
import sys

if len(sys.argv) != 2:
    print("ERROR: To use './btree-compress.py FILENAME'" % input_filename)
    sys.exit(1)

btree_filename = sys.argv[1]
btree_small_filename = btree_filename + '.small'

if not btree_filename.endswith('.btree'):
    print("ERROR: %s does not end with .btree" % btree_filename)
    sys.exit(1)

if not os.path.isfile(btree_filename):
    print("ERROR: %s does not exist" % btree_filename)
    sys.exit(1)

with open(btree_filename, 'rb') as fh_btree:
    with open(btree_small_filename, 'w+b') as fh_btree_small:
        recopy_sbplus(fh_btree, fh_btree_small)
