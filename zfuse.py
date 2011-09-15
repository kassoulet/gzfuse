#!/usr/bin/env python
# 
# zfuse, simple transparent decompression for fuse
# 
# 
# Copyright (c) 2011 Gautier Portet <kassoulet+gmail>
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
from os.path import realpath
from sys import argv #, exit
from threading import Lock
import gzip
import os

# http://code.google.com/p/fusepy
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

base = {}

def convert_filename(filename):
    if filename.endswith('.gz'):
        original = filename
        filename = filename[:-len('.gz')]
        base['/' + filename] = '/' + original
    return filename
    

class Loopback(Operations, LoggingMixIn):    

    chmod = os.chmod
    chown = os.chown
    fsync = None
    listxattr = 1
    mkdir = os.mkdir
    mknod = None
    getxattr = None
    readlink = 3
    rmdir = None
    statfs = None
    symlink = None
    unlink = os.unlink
    utimens = os.utime

    def __init__(self, root):
        self.root = realpath(root)
        self.rwlock = Lock()
        self.files = {}
    
    def __call__(self, op, path, *args):
        if path in base:
            path = base[path]
        return super(Loopback, self).__call__(op, self.root + path, *args)
    
    def access(self, path, mode):
        print 'access:', path, mode
        if not os.access(path, mode):
            raise FuseOSError(EACCES)
    
    def create(self, path, mode):
        self.files[path+'.gz'] = gzip.open(path+'.gz', 'wb')
        path = path[len(self.root)+1:]
        convert_filename(path+'.gz')
        return 1
    
    def flush(self, path, fh):
        if path not in self.files:
            print 'flush error:', path, 'not in', self.files 
            return
        return self.files[path].flush()

    def getattr(self, path, fh=None):
        print 'getattr:', path, fh
        st = os.lstat(path)
        d = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        print d
        if path.endswith('.gz'):
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
        return d
    
    def link(self, target, source):
        print 'link:', source, '->', target
        raise NotImplementedError
        return os.link(source, target)
    
    def open(self, path, flags):
        mode = 'r'
        if flags & os.O_WRONLY:
            mode = 'w'
        if flags & os.O_APPEND:
            mode = 'a'
        if path.endswith('.gz'):
            self.files[path] = gzip.open(path, mode+'b3')
        else:
            self.files[path] = open(path, mode+'b')
        print 'open:', path, mode
        return 1        
        
    def read(self, path, size, offset, fh):
        print 'read: %s %s %s' % (path, offset, size)
        if path not in self.files:
            print 'read error:', path, 'not in', self.files
        with self.rwlock:
            self.files[path].seek(offset, 0)
            return self.files[path].read(size)
    
    def readdir(self, path, fh):
        print 'readdir:', path
        return ['.', '..'] + [convert_filename(f) for f in os.listdir(path)]

    def release(self, path, fh):
        if path not in self.files:
            print 'release error:', path, 'not in', self.files
            return
        r = self.files[path].close()
        del self.files[path]
        return r 
        
    def rename(self, old, new):
        print 'rename:', old, '->', self.root + new
        return os.rename(old, self.root + new)

    def truncate(self, path, length, fh=None):
        if length > 0:
            print 'truncate:', path, length
            raise NotImplementedError
        open(path, 'wb').close()
    
    def write(self, path, data, offset, fh):
        print 'write: %s %s %s' % (path, offset, len(data))
        with self.rwlock:
            self.files[path].seek(offset, 0)
            return self.files[path].write(data)
    

if __name__ == "__main__":
    if len(argv) != 3:
        print 'usage: %s <root> <mountpoint>' % argv[0]
        exit(1)
    fuse = FUSE(Loopback(argv[1]), argv[2], 
                foreground=True, debug=False, nothreads=True)
    
    
    
