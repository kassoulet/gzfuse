#!/usr/bin/env python

import sys,os,random, time

def timed(name, size, command):
    times = []
    for i in range(1):
        clearcache()
        start = time.time()
        os.system(command)
        end = time.time()
        times.append(end-start)
    delta = min(times)
    print '%s %.2f MB in %.2fs (%.2fMB/s)' % (name, size/1024/1024, delta, size/1024/1024/delta)

def benchmark(filename, folder=None):
    if not folder:
        folder = '.'
    folder += '/'

    gen(filename, folder)

    #print '\n=== %s ===' % filename
    clearcache()
    size = float(os.path.getsize('test/original/%s.raw' % filename))

    timed('native reading', size, 'cat test/original/%s.raw > /dev/null' % filename)
    timed('native writing', size, 'cp test/original/%s.raw test/original/%s.copy' % (filename, filename))

    timed('gzip', size, 'gzip -c test/original/%s.copy > /dev/null' % filename)
    os.system('gzip -c test/original/%s.copy > test/original/%s.copy.gz' % (filename, filename))
    timed('gunzip', size, 'gunzip test/original/%s.copy.gz -c > /dev/null' % filename)

    timed('zfuse reading', size, 'cat test/mounted/%s > /dev/null' % filename)
    timed('zfuse writing', size, 'cp test/original/%s.raw test/mounted/%s.write' % (filename, filename))


def _test_speed(folder=None):
    #benchmark('big', folder)
    benchmark('big')


if __name__ == '__main__':

    #for folder in os.listdir(sys.argv[1]):
    #    print '\n', folder
    #    test_speed(sys.argv[1]+'/'+folder)
    #test_speed()
