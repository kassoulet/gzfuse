#!/usr/bin/env python
"""
 - stress tests, many concurent accesses, checking integrity
   maybe by storing the md5 as filename
 - test seeks
 - test speed

 benchmark avec plusieurs liens vers des repertoires (SSD,HDD,USB)
 et test avec et sans zfuse
"""

import sys,os,random, time

def mkdir(folder):
    try:
        os.mkdir(folder)
    except OSError:
        pass


def gen(filename, folder):
    os.chdir(folder)
    mkdir('test')
    mkdir('test/original')
    mkdir('test/mounted')
    words = [w.strip() for w in file('/usr/share/dict/words')]

    f = file(folder+'test/original/%s.raw' % filename, 'wb')
    for i in range(1000000):
        for j in range(10):
            f.write(random.choice(words)+' ')
        f.write('\n')
    f.close()
    os.system('gzip -fc '+folder+'test/original/%s.raw > ' % filename+folder+'test/original/%s.gz' % filename)


def test_small():
    assert os.path.ismount('test/mounted')
    assert os.path.exists('test/mounted/test')
    assert os.path.getsize('test/mounted/test') == 10
    assert os.path.getmtime('test/mounted/test') == os.path.getmtime('test/original/test.gz')


def test_big():
    assert os.path.ismount('test/mounted')
    assert os.path.exists('test/mounted/big')
    assert os.path.getsize('test/mounted/big') == os.path.getsize('test/mounted/big.raw')
    #print os.path.getmtime('test/mounted/big')
    #print os.path.getmtime('test/original/big.gz')
    #print os.path.getmtime('test/original/big.raw')
    assert os.path.getmtime('test/mounted/big') == os.path.getmtime('test/original/big.gz')
    #assert os.path.getmtime('test/mounted/big') == os.path.getmtime('test/original/big.raw')


def test_reverse():

    f = file('test/mounted/reverse', 'wb')
    f.write('zfuse rocks!')
    f.close()
    assert os.path.exists('test/mounted/reverse')
    assert os.path.exists('test/original/reverse.gz')



errors = 0
tests = 0

for f in [f for f in globals().copy() if f.startswith('test_')]:
    print f,
    tests += 1
    globals()[f]()
    try:
        globals()[f]()
        print 'OK'
    except AssertionError, e:
        #print e.message, e.args, dir(e)
        errors += 1
        print 'FAILED'

print '%d test(s), %d error(s)' % (tests, errors)


