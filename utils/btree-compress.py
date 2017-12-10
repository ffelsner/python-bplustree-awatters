#!/usr/bin/env python2

"""
Use recopy_sbplus to rebuild a .btree so that it takes less disk space.
"""

from bplustree import recopy_sbplus
import logging
import os
import sys


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))


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
