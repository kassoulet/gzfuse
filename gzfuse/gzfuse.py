#!/usr/bin/env python
# 
# gzfuse - simple, transparent gz decompression for fuse
# 
# 
# Copyright (c) 2012 Gautier Portet <kassoulet+gmail>
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from errno import EACCES
from os.path import realpath, join
from sys import argv, stdout
from threading import Lock
import gzip
import os

# http://code.google.com/p/fusepy
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

#base = {}

def log(*args):
    return
    print ' '.join(str(s) for s in args)
    stdout.flush()

def error(*args):
    print ' '.join(str(s) for s in args)
    stdout.flush()
    raise SystemExit

def convert_filename(filename, path):
    if filename.endswith('.gz'):
        original = filename
        filename = filename[:-len('.gz')]
        #base[join(path, filename)] = join(path, original)
    return filename

counter = 0
really = 0

class Loopback(Operations):

    fsync = None
    listxattr = 1
    mknod = None
    getxattr = None
    readlink = 3
    rmdir = None
    statfs = None
    symlink = None
    utimens = os.utime

    def __init__(self, root):
        self.root = realpath(root)
        #self.rwlock = Lock()
        self.fileslock = Lock() # TODO: useful ?
        self.files = {}
        self.content = {}
    
    def __call__(self, op, path, *args):
        #log('call: %s %s %s' % (op, path, args))
        #if path in base:
        #    print ' ', path, '->' ,base[path]
        #    path = base[path]
        if not os.path.exists(self.root + path):
            if os.path.exists(self.root + path + '.gz'):
                path += '.gz'
        return super(Loopback, self).__call__(op, self.root + path, *args)
    
    def access(self, path, mode):
        log('access:', path, mode)
        if not os.access(path, mode):
            raise FuseOSError(EACCES)
    
    def flush(self, path, fh):
        return self.files[fh].flush()

    def getattr(self, path, fh=None):
        log('getattr:', path, fh)
        st = os.lstat(path)
        d = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        if path.endswith('.gz'):
            # read file size from gz header
            with open(path, 'rb') as f:
                size = 0
                try:
                    f.seek(-4, 2)
                    s = f.read()
                    for i in range(4):
                        size += ord(s[i]) * (1 << (8 * i))
                except IOError:
                    pass
                d['st_size'] = size
        d['st_mode'] &= 0xffffff6d # remove write attr
        return d
    
    def open(self, path, flags):
        mode = 'r'
        if flags & os.O_WRONLY:
            error('Write mode is not supported!')
            return 0
            #mode = 'w'
        if flags & os.O_APPEND:
            error('Append mode is not supported!')
            return 0
            #raise NotImplementedError
        if path.endswith('.gz'):
            f = gzip.open(path, mode+'b3')
        else:
            f = open(path, mode+'b')
        
        with self.fileslock:
            global counter
            counter += 1
            self.files[counter] = f
            #if not path in self.content:
            #    global really
            #    really += 1
            #    self.content[path] = f.read()
            fh = counter
        log('open:', path, mode, fh)
        return fh     
        
    def read(self, path, size, offset, fh):
        log('read: %s %s %s %s' % (path, offset, size, fh))
        #with self.rwlock:
        #return self.content[path][offset:offset+size]
        self.files[fh].seek(offset)
        return self.files[fh].read(size)
    
    def readdir(self, path, fh):
        relpath = path[len(self.root):]
        log('readdir:', path)
        l = ['.', '..'] + [convert_filename(f, relpath) for f in os.listdir(path)]
        return l

    def release(self, path, fh):
        log('close: %s %s' % (path, fh))
        r = self.files[fh].close()
        with self.fileslock:
            del self.files[fh]
        return r 
            

def main():
    if len(argv) != 3:
        print 'usage: %s <root> <mountpoint>' % argv[0]
        exit(1)
    fuse = FUSE(Loopback(argv[1]), argv[2], 
                foreground=True, debug=False, nothreads=True)
    
    print 'gzfuse exited. %d files read, %d files really read' % (counter, really)
    
if __name__ == "__main__":
    main()
