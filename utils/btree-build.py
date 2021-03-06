#!/usr/bin/env python3

"""
Read a file of the format:

key1:value1
key2:value2

and save it as a .btree file
"""

from bplustree import SBplusTree
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

log.info("Scan the file to find the key_size")
max_key_size = 0

with open(input_filename, 'r') as fh:

    for (line_number, line) in enumerate(fh):
        (key, value) = line.strip().split(':')

        key_size = len(key)

        if key_size > max_key_size:
            max_key_size = key_size

assert max_key_size > 0, "key_size %s is invalid" % max_key_size
log.info("max_key_size   : %2d bytes" % max_key_size)


with open(btree_filename, 'w+b') as fh_btree:
    B = SBplusTree(fh_btree, position=0, nodesize=200, keylen=max_key_size)
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
