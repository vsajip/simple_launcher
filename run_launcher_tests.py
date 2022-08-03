#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Vinay Sajip
#
import argparse
import datetime
import logging
import os
import subprocess
import sys
import time

import psutil

DEBUGGING = 'PY_DEBUG' in os.environ

logger = logging.getLogger(__name__)

def message(s):
    tod = datetime.datetime.now().strftime('%H:%M:%S')
    print('%s %s' % (tod, s), file=sys.stderr)

def dump_process_tree(pp, descendants, level=1):
    descendants.append(pp)
    indent = level * '  '
    print('%s%s %s' % (indent, pp.pid, pp.cmdline()), file=sys.stderr)
    for kid in pp.children():
        dump_process_tree(kid, descendants, level + 1)

def test_executable(options, cmd, descr):
    message('Running %s ...' % descr)
    p = subprocess.Popen(cmd)
    time.sleep(0.5)
    pp = psutil.Process(p.pid)
    message('Process tree:')
    descendants = []
    dump_process_tree(pp, descendants)
    message('Waiting %s secs ...' % options.delay)
    time.sleep(options.delay - 0.5)
    message('Trying to stop %s with pid %s ...' % (descr, p.pid))
    p.kill()
    message('Waiting 500 msecs ...')
    time.sleep(0.5)
    rc = p.poll()
    if rc is None:
        message('The %s is still running' % descr)
        raise ValueError('Failed to stop %s' % descr)
    alive = []
    for descendant in descendants:
        try:
            s = descendant.status()
            message('Descendant remaining: %s' % descendant)
            alive.append(descendant)
        except psutil.NoSuchProcess:
            pass
    if alive:
        raise ValueError('There are still %d descendants alive' % len(alive))
    message('%s stopped with return code: %s' % (descr, rc))

def main():
    fn = os.path.basename(__file__)
    fn = os.path.splitext(fn)[0]
    lfn = os.path.expanduser('~/logs/%s.log' % fn)
    if os.path.isdir(os.path.dirname(lfn)):
        logging.basicConfig(level=logging.DEBUG, filename=lfn, filemode='w',
                            format='%(message)s')
    adhf = argparse.ArgumentDefaultsHelpFormatter
    ap = argparse.ArgumentParser(formatter_class=adhf, prog=fn)
    aa = ap.add_argument
    # aa('input', metavar='INPUT', help='File to process')
    aa('--delay', '-d', type=int, default=5, help='Delay before trying to stop')
    aa('--console', '-c', default=False, action='store_true',
       help='Test console executable only')
    aa('--windowed', '-w', default=False, action='store_true',
       help='Test windowed executable only')
    aa('-s', '--suffix', default='v', help='Suffix for executables')
    options = ap.parse_args()
    if not options.console and not options.windowed:
        options.all = True
    else:
        options.all = False
    if options.console or options.all:
        cmd = [os.path.join('test', 'test%s.exe' % options.suffix), '10']
        test_executable(options, cmd, 'console executable')
    if options.windowed or options.all:
        cmd = [os.path.join('test', 'test%sw.exe' % options.suffix)]
        test_executable(options, cmd, 'windowed executable')

if __name__ == '__main__':
    try:
        rc = main()
    except KeyboardInterrupt:
        rc = 2
    except Exception as e:
        if DEBUGGING:
            s = ' %s:' % type(e).__name__
        else:
            s = ''
        sys.stderr.write('Failed:%s %s\n' % (s, e))
        if DEBUGGING: import traceback; traceback.print_exc()
        rc = 1
    sys.exit(rc)
