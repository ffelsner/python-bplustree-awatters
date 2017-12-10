#!/usr/bin/env python3

"""
Lookup KEY in FILENAME
"""

from bplustree import caching_SBPT
import logging
import os
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

if len(sys.argv) != 3:
    print("ERROR: To use './btree-lookup.py FILENAME KEY'" % input_filename)
    sys.exit(1)

btree_filename = sys.argv[1]
key = sys.argv[2]

if not btree_filename.endswith('.btree'):
    print("ERROR: %s does not end with .btree" % btree_filename)
    sys.exit(1)

if not os.path.isfile(btree_filename):
    print("ERROR: %s does not exist" % btree_filename)
    sys.exit(1)

with open(btree_filename, 'rb') as fh:
    B = caching_SBPT(fh)
    B.open()
    log.info("search start")
    value = B[key]
    print("key %s value is %s" % (key, value))
    log.info("search end")
