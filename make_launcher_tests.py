# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2022 Vinay Sajip.
#
import argparse
import datetime
import io
import os
import sys
import zipfile

MAIN = r'''
import argparse
import sys
import time

print(sys.version)
print(sys.argv)
print(sys.executable)
print('\nPress Ctrl-C to exit:')
parser = argparse.ArgumentParser()
parser.add_argument('cleanup', default=4, type=int, metavar='CLEANUP',
                    nargs='?', help='Cleanup time in seconds')
options = parser.parse_args()
DELAY = options.cleanup
try:
    while True:
        pass
except KeyboardInterrupt:
    print('Ctrl-C seen, cleaning up (should take %d secs) ...' % DELAY)
    for i in range(DELAY):
        print('%d steps to go ...' % (DELAY - i))
        time.sleep(1)
    print('Cleanup done.')
'''

MAINW = r'''
import ctypes
import sys

MB_OK = 0

s = '\n'.join([sys.version, str(sys.argv), sys.executable])
ctypes.windll.user32.MessageBoxW(0, s, 'System Info', MB_OK)
'''

# Use a fixed time to have a reproducible archive as far as possible
ZIP_TIMESTAMP = datetime.date(2000, 1, 1).timetuple()[:6]

LAUNCHER_LOCATION = r'env\Lib\site-packages\distlib'
PYTHON_LOCATION = os.path.abspath(r'env\Scripts\python.exe').lower()

def main():
    fn = os.path.basename(__file__)
    fn = os.path.splitext(fn)[0]
    adhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=adhf, prog=fn)
    parser.add_argument('-p', '--python', default=PYTHON_LOCATION,
                        help='Use this in the shebang (must contain the text "python.exe"')
    parser.add_argument('-o', '--outdir', default='test',
                        help='Write files here')
    parser.add_argument('-s', '--suffix', default='v',
                        help='Suffix for executables')
    options = parser.parse_args()
    script_data = MAIN.strip().encode('utf-8')
    wscript_data = MAINW.strip().encode('utf-8')
    archive_data = io.BytesIO()
    warchive_data = io.BytesIO()
    zinfo = zipfile.ZipInfo(filename='__main__.py',
                            date_time=ZIP_TIMESTAMP)
    with zipfile.ZipFile(archive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zinfo, script_data)
    with zipfile.ZipFile(warchive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(zinfo, wscript_data)
    # hard to escape double quotes in command line, so replace
    # single quotes with double
    options.shebang = options.python.replace('\'', '"')
    shebang = ('#!%s\n' % options.shebang).encode('utf-8')
    wshebang = ('#!%s\n' % options.shebang.replace('python.exe', 'pythonw.exe')).encode('utf-8')
    fn = os.path.join(LAUNCHER_LOCATION, 't64.exe')
    if os.path.exists(fn):
        with open(fn, 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + shebang + archive_data.getvalue()
        ofn = os.path.join(options.outdir, 'test%s.exe' % options.suffix)
        with open(ofn, 'wb') as f:
            f.write(data)
        print('wrote %s using launcher %s and shebang %s' % (ofn, fn, shebang.rstrip().decode('utf-8')))
    fn = os.path.join(LAUNCHER_LOCATION, 'w64.exe')
    if os.path.exists(fn):
        with open(fn, 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + wshebang + warchive_data.getvalue()
        ofn = os.path.join(options.outdir, 'test%sw.exe' % options.suffix)
        with open(ofn, 'wb') as f:
            f.write(data)
        print('wrote %s using launcher %s and shebang %s' % (ofn, fn, wshebang.rstrip().decode('utf-8')))


if __name__ == '__main__':
    sys.exit(main())
