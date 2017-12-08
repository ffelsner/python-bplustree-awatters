# bplustree

I found this implementation at
http://www.pha.com.au/kb/index.php/Python_-_bplustree.py

I ran autopep against it and did some minor style cleanup but other than that
it is the same as originaly written by Aaron Watters. I did attempt to update
it to python3 via 2to3 but it barfed on the keys_indices() map() call on line
605 and I haven't had time to dig into why it failed. So for now this will only
work with python2.

-Daniel Walton

B+tree implementation
=====================
B+ trees are an efficient index structure for mapping 
a dictionary type object into a disk file.  All keys for
these dictionary structures are strings with a fixed
maximum length.  The values can be strings or
integers (often representing seek positions in a secondary
file) depending on the implementation.

B+ trees can be useful for storing large mappings on disk
in such a way that a small number of keys/values can be
retrieved very quickly (with very few disk accesses).
B+ trees can also be useful for sorting a very large number
(millions) of records by unique string key values.

In this implementation all keys must
not exceed the maximum length for a
given tree.  For string values there is no limitation on
size of content.  Note that in my tests updates are
2-3 times slower than retrieves, except for walking
which is much faster than normal retrieves.

As an add-on this module also provides a dbm compatible
interface that permits arbitrary length keys and values.
See below.

Provided here are several implementations:
```
BplusTree():
  defines a mapping from strings to integers.

caching_BPT():
  subclass of BplusTree that caches key,value
  pairs already seen.  This one cannot be updated.
  Construct a compatible index file using BplusTree
  and for read only access that touches a manageable
  number of keys, reopen the file using caching_BPT.

SBplusTree():
  defines a mapping from strings to strings.
  Updatable, but overwrites or deletions will
  leave "unreachable garbage" in the "value space"
  of the index file.  Use recopy_sbplus() to
  recopy the file, eliminating the garbage.

caching_SBPT():
  analogous to caching_BPT, but mapping to strings.
```

File creation:
==============
To create an index file do the following:
```
  file = open(filename, "w+b")
  B = SBplusTree(file, seek_position, nodesize, keymax)
  B.startup()
```

where seek_position is the seek_position where to "start"
the tree (usually the start of file, 0), nodesize is the
number of keys to keep at each node of the tree (pick an
even number between 2 and 255), and keymax is the maximum
size for the string keys in the mapping.

When choosing nodesize remember that larger nodesizes
make Python do more work and the file system do less work.
I think 212 is probably a pretty good number.  Of course
choose keymax to be as large as you will need.  A too large
key size, however, may waste considerable space in the file.

Now that you have a tree you can populate it with values
just like a dictionary.
```
   B["this"] = "that"
   B["willy"] = "wonka"
   x = B["this"]
   del B["this"]
   print len(B)
   ...
   f.close()
```

The supported dictionary operations are indexed retrieval
B[k], indexed assignment B[k] = v, key deletion del B[k] and
length len(B).  Retrieval and deletion will raise KeyError
on absent key.  Assignment will raise ValueError if the key
is too large.

B.keys(), B.values(), B.items() are not directly
supported, but see "Walking" below.

Note that the "basic" B-plus tree implementations only accept and
return integers as values.  The SB-plus implementation will
accept anything as values, but will use the str(x) function
to convert them to a string before storing the value in the
file.  The value returned will always be the string value
stored.  IE
```
   B["okeydoke"] = 23
   print `B["okeydoke"]`
```

prints "'23'", with the quotes.  The controlling
application must control the
serialization/deserialization of values if it needs to store
something other than strings.

Read only file access:
======================
Once an index file exists it can be re-opened in "read only"
mode.
```
   f = open(filename, "rb")
   B = caching_SBPT(f)
   B.open()
   print B["willy"]
```

Note that the configuration parameters for the tree are
determined from a "file header".  Note however that a file
written to store integers using BplusTree should not be opened
for strings using SBplusTree or undefined and undesirable
behaviour will result.  Opening an SBplusTree as a BplusTree
is not advisable either.

If the seek position for the start of the tree is anything
other than 0, it must be specified:
```
   B = caching_SBPT(f, position)
```

or undefined behaviour will result.

In this mode, retrieval and walking are permitted, but attempts
to modify the structure will cause an exception.  In this mode the
programmer may prefer to use the "caching" versions if they expect
to retrieve the same keys many times and if the number of keys to
touch is not huge (say, in the millions).

Re-open for modification:
=========================
An existing index file can also be reopened for modification.
```
   f = open(filename, "r+b")
   B = SBplusTree(f)
   B.open()
   B["this"] = "is fun!"
   ...
   f.close()
```

Again, modifications are disallowed for cached trees.

Walking:
========
One of the neat features of B-plus trees is that they keep
their keys in sorted order.  Hence it is easy and efficient
to retrieve the keys/values sorted by the keys, and also to
do range queries.

To support this feature the tree implementations provide
a "walker" interface.
```
   walker = tree.walker(lowerkey, includelower,
                        upperkey, includeupper)
   while walker.valid:
      print (walker.current_key(), walker.current_value())
      walker.next()
   walker.first()
```

Or to traverse all pairs in key-sorted order
```
   walker = tree.walker()
   while walker.valid:
      print (walker.current_key(), walker.current_value())
      walker.next()
   walker.first()
```

The lowerkey/upperkey parameters indicate where to start/end
walking (interpreted as the beginning/end if they are
omitted or set to None) and includelower indicates whether
to include the lower value if it is present in the tree,
if not the next greater key will be the start position.

For example to walk from key "m" (or just past it if absent)
to the end:
```
    w = tree.walker("m", 1)
```

or to walk between "mzzz" and "nzzz" not inclusive:
```
    w = tree.walker("mzzz", 0, "nzzz", 0)
```

or walk from the beginning to "m", not inclusive
```
    w = tree.walker(None, None, "m", 0)
```

Here w.current_key() and w.current_value() retrieve the current
key and value respectively, w.next() moves to the next pair, if there is one
and w.valid indicates whether there is a current pair, and
w.first() resets the walker to the first pair, if there is one.
At initialization the walker is already at the first pair, if
it exists.

Multiaccess optimizations:
==========================

To make updates and retrievals run faster you can enable/disable
a tree-global least-recently-used fifo mechanism which reduces
reads and writes, but be *sure* to disable it before closing any
BTree file that has been modified, or the tree may well become
corrupt
```
    try:
       B.enable_fifo()
       do_updates(B)
    finally:
       B.disable_fifo()
```

The fifo may also improve performance for read only access,
but it is not important to disable the mechanism later.
The optimizations help most when key accesses are localized.
(ie, a bunch of inserts with keys starting "abc..."
or 10000 inserts in [almost] key-sorted order).
For only one access, it's no help at all!  The fifo mechanism
will not help for walking, so don't do it if you will only walk
a portion of the tree once.  You might want to try putting
various values as the optional argument to enable_fifo, eg,
B.enable_fifo(1000) (but that's probably past the diminishing returns
point...).  Large fifos will consume lots of "core" memory.

Trash compacting
================

The functions recopy_bplus(f1, f2) and recopy_sbplus(f1, f2)
recopy open "rb" file f1 to (open "w+b")
file f2 for BplusTrees and SBplusTrees respectively.  The
copy f2 will have no "garbage" and almost all leaf nodes will be
full.  This can result in reducing file size by about 1/3.
Both files must have headers at seek 0 and hold nothing but
the tree nodes and tree data.  Also look at recopy_tree(t1, t2).

DBM compatibility
=================

As an application of SBplusTree this module also provides
a plug-compatible implementation of the standard python dbm
style functionality, except that the "mode" parameter is not
supported on initialization.  See the Python Lib manual entry
on dbm.  Both keys and values may be of *arbitrary* length in
this case, but keys are not kept in key-sorted order and
overwrites and key collisions will result in unused garbage
in the file (keys and values occur as SBplustree "values"
using a PORTABLE bucket hashing scheme).
```
   d = dbm(filename, flag)
```

creates a dictionary like structure with d[key]=value, x=d[key],
d.has_key(key), del d[key], len(d), and d.keys().  Also
after any modification be sure that d gets explicitly
closed d.close() or the file *may* become corrupt.
Also, d.copy(otherfilename, "c") will create a more
compact copy of d in another file with garbage discarded.
The dbm implementation uses a very large fifo, so many accesses
may consume a lot of "core" memory.

DBM comparison
==============
An alternative to this module is gdbm or dbm for file
indexing -- both supported by available Python extension
modules.

Expect dbm to be generally faster than this module, but
remember:
- dbm doesn't do key-sorted walking.
- dbm often isn't portable across machines.
- dbm isn't written in Python (ie, requires an extension module).
- dbm sometimes doesn't allow arbitrary value lengths
  (but gdbm allows arbitrary length keys and values...)

whereas this module does/is.  I don't know precisely how
much faster dbm is, but for some types of use it may turn
out to actually be slower, for all I know.  Please let
me know!  Probably the most compelling advantage is that
the index files generated by this module are portable across
platforms.

Fun
===
For fun or debugging try tree.dump().
There is also a test suite for the module at the
bottom (test() and retest()) which create a test index
called "test" in the current directory.  Also testdbm().

Caveats:
========
NOTE: only the standard string ordering is supported for
  walking at present.  This could be fixed...

WARNING: Never modify a tree while it is being walked.  Always
  recreate all walkers after a tree modification.
  NEVER open the same tree for modification twice!
  ALWAYS make sure a modified tree has disabled the fifo and
  the file has been closed before reopening the tree.

WARNING: This implementation has no support for concurrent
  modification.  It is designed for "write once by one process",
  "read many by (possibly) several processes, but not with
  concurrent modification."

WARNING: If during modification any exception other than a KeyError/ValueError
  is not caught, the indexed file structure *may* become corrupt (because
  some operations completed and others didn't).  Walking all values
  of an index or B.dump() may detect some corrupt states (***Note I should write
  a sanity-check routine***)

WARNING: As noted above an overwrite or delete for a SBTree (mapping
  to strings) will leave unreachable junk in the "value space" of
  the index.  See above.

This code is provided for arbitrary use, but without warrantee of
any kind.  At present it seems to work, but I'll call it an beta
until it's better tested.

Aaron Watters, arw@pythonpros.com
http://starship.skyport.net/crew/aaron_watters
http://www.pythonpros.com
