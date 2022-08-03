#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Red Dove Consultants Limited
#
import argparse
import datetime
import io
import logging
import os
import struct
import sys
import zipfile

DEBUGGING = 'PY_DEBUG' in os.environ

logger = logging.getLogger(__name__)


def _examine_possible_archive(s):
    launcher = shebang = data = None
    try:
        with open(s, 'rb') as f:
            all_data = f.read()
        pos = all_data.rfind(b'PK\x05\x06')
        if pos >= 0:
            end_cdr = all_data[pos + 12:pos + 20]
            cdr_size, cdr_offset = struct.unpack('<LL', end_cdr)
            arc_pos = pos - cdr_size - cdr_offset
            data = all_data[arc_pos:]
            if arc_pos > 0:
                pos = all_data.rfind(b'#!', 0, arc_pos)
                if pos >= 0:
                    shebang = all_data[pos:arc_pos]
                    if pos > 0:
                        launcher = all_data[:pos]
    except Exception as e:
        pass
    return launcher, shebang, data

def dump_archive(data, prefix):
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        infos = zf.infolist()
        for info in infos:
            dt = datetime.datetime(*info.date_time)
            print('%s%s %-6s %s' % (prefix, dt, info.file_size, info.filename))

def main():
    fn = os.path.basename(__file__)
    fn = os.path.splitext(fn)[0]
    lfn = os.path.expanduser('~/logs/%s.log' % fn)
    if os.path.isdir(os.path.dirname(lfn)):
        logging.basicConfig(level=logging.DEBUG, filename=lfn, filemode='w',
                            format='%(message)s')
    adhf = argparse.ArgumentDefaultsHelpFormatter
    ap = argparse.ArgumentParser(formatter_class=adhf, prog=fn,
                                 description='Compare two executables with launchers.')
    aa = ap.add_argument
    aa('launcher1', metavar='LAUNCHER1', help='Path to first launcher executable')
    aa('launcher2', metavar='LAUNCHER2', help='Path to second launcher executable')
    options = ap.parse_args()
    launcher1, shebang1, data1 = _examine_possible_archive(options.launcher1)
    launcher2, shebang2, data2 = _examine_possible_archive(options.launcher2)
    if launcher1 != launcher2:
        print('Launchers differ:')
        if launcher1:
            print('  1st executable has a launcher of size %d.' % len(launcher1))
        if launcher2:
            print('  2nd executable has a launcher of size %d.' % len(launcher2))
    if shebang1 != shebang2:
        print('Shebangs differ:')
        s = None if shebang1 is None else shebang1.rstrip().decode('utf-8')
        print('  1st executable shebang: %s' % s)
        s = None if shebang2 is None else shebang2.rstrip().decode('utf-8')
        print('  2nd executable shebang: %s' % s)
    if data1 != data2:
        print('Archives differ:')
        if data1:
            print('  1st executable archive contents:')
            dump_archive(data1, '    ')
        if data2:
            print('  2nd executable archive contents:')
            dump_archive(data2, '    ')

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
