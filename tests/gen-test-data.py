#!/usr/bin/env python

import sys,os,random, time
import atexit

def mkdir(folder):
    try:
        os.mkdir(folder)
    except OSError:
        pass

content = '0123456789'
content_mtime = None


def populate():
    print 'generating test data...'
    os.system('rm -rf test')
    mkdir('test')
    mkdir('test/original')
    mkdir('test/mounted')
    f = file('test/original/test', 'wb')
    f.write(content)
    f.close()
    global content_mtime
    content_mtime = os.path.getmtime('test/original/test')
    os.system('gzip -f test/original/test')
    
    words = [w.strip() for w in file('/usr/share/dict/words')]

    f = file('test/original/big.raw', 'wb')
    for i in range(1000000):
        for j in range(10):
            f.write(random.choice(words)+' ')
        f.write('\n')
    f.close()
    os.system('gzip -fc test/original/big.raw > test/original/big.gz')

    f = file('test/original/empty.raw', 'wb')
    for i in xrange(1024*100):
        f.write('0'*1024)
    f.close()
    os.system('gzip -fc test/original/empty.raw > test/original/empty.gz')
    
populate()

