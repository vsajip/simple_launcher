# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2021 Vinay Sajip.
#
import argparse
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

def main():
    fn = os.path.basename(__file__)
    fn = os.path.splitext(fn)[0]
    adhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=adhf, prog=fn)
    parser.add_argument('-s', '--shebang', default='c:/python38/python.exe -u',
                        help='Use this in the shebang')
    parser.add_argument('-o', '--outdir', default='test',
                        help='Write files here')
    options = parser.parse_args()
    script_data = MAIN.strip().encode('utf-8')
    wscript_data = MAINW.strip().encode('utf-8')
    archive_data = io.BytesIO()
    warchive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('__main__.py', script_data)
    with zipfile.ZipFile(warchive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('__main__.py', wscript_data)
    # hard to escape double quotes in command line, so replace
    # single quotes with double
    options.shebang = options.shebang.replace('\'', '"')
    shebang = ('#!%s\n' % options.shebang).encode('utf-8')
    wshebang = ('#!%s\n' % options.shebang.replace('python.exe', 'pythonw.exe')).encode('utf-8')
    if os.path.exists('x64/Debug/CLISimpleLauncher.exe'):
        with open('x64/Debug/CLISimpleLauncher.exe', 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + shebang + archive_data.getvalue()
        ofn = os.path.join(options.outdir, 'test.exe')
        with open(ofn, 'wb') as f:
            f.write(data)
        print('wrote %s' % ofn)
    if os.path.exists('x64/Debug/GUISimpleLauncher.exe'):
        with open('x64/Debug/GUISimpleLauncher.exe', 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + wshebang + warchive_data.getvalue()
        ofn = os.path.join(options.outdir, 'testw.exe')
        with open(ofn, 'wb') as f:
            f.write(data)
        print('wrote %s' % ofn)


if __name__ == '__main__':
    sys.exit(main())
