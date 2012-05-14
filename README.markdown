
gzfuse - simple, transparent gz decompression for fuse
================================================

gzfuse is read-only gunzip loopback for fuse, allowing you to read 
transparently from a folder full of compressed files.

Usage
-----

Just run `gzfuse.py original-folder gunzip-folder`, and now all .gz files 
in `original-folder` are accessible in `gunzip-folder`, as they were plain
files.


Why?
----

Yeah, you can ask why doing a gunzip loopback for fuse, since there are already
a bunch of transparent unpackers for fuse...
Just look at the implementation. It's dead simple. So why not?
Also, all others unpackers have their own format, and you can't be sure if you
will really be able to read your files after a while.
With gzfuse the problem is solved: it's just plain old gzip files!


Limitations
----------

The current gzfuse implementation should be considered *experimental*. It does
require a lot more testing. And a rewrite in C, as it's currently written in
Python.

So, to put here a nice list. gzfuse is currently:

- not enough tested
- rather slow
- single-theaded
- read-only

All these limitations are to be fixed in the future if there is an use for it.


Test case
--------

The test folder is linux-3.3.3. 40,358 items, totalling 445.2 MB.
After gzip, 127.3 MB.

    # compress all files
    $ find linux-3.3.3-gz -type f -exec gzip {} \;
    
    # mount gzfuse folder
    $ gzfuse.py linux-3.3.3-gz linux-3.3.3-gzfuse

    # read all files
    $ time find linux-3.3.3 -type f -exec cat {} \; > /dev/null

    real	1m33.291s
    user	0m7.132s
    sys	0m28.132s

    # read all files, transparent decompression
    $ time find linux-3.3.3-gzfuse -type f -exec cat {} \; > /dev/null

    real	1m59.485s
    user	0m9.206s
    sys	0m28.275s

