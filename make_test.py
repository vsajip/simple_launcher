# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Vinay Sajip.
#
import argparse
import io
import os
import sys
import zipfile

MAIN = '''
import sys
print(sys.version)
print(sys.argv)
print(sys.executable)
'''

MAINW = r'''
import ctypes
import logging
import sys

logging.basicConfig(level=logging.DEBUG, filename='c:/temp/testw.log',
                    filemode='w')
try:
    s = '\n'.join([sys.version, str(sys.argv), sys.executable])
    ctypes.windll.user32.MessageBoxW(0, s, 'System Info', 1)
except:
    logging.exception('Failed')
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shebang', help='Specify shebang to add')
    parser.add_argument('-o', '--output', help='Specify output filename')
    options = parser.parse_args()
    script_data = MAIN.strip().encode('utf-8')
    wscript_data = MAINW.strip().encode('utf-8')
    archive_data = io.BytesIO()
    warchive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('__main__.py', script_data)
    with zipfile.ZipFile(warchive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('__main__.py', wscript_data)
    if options.shebang is None:
        options.shebang = 'c:/python38/python.exe -u'
    else:
        # hard to escape double quotes in command line, so replace
        # single quotes with double
        options.shebang = options.shebang.replace('\'', '"')
    shebang = ('#!%s\n' % options.shebang).encode('utf-8')
    wshebang = ('#!%s\n' % options.shebang.replace('python.exe', 'pythonw.exe')).encode('utf-8')
    if options.output is None:
        options.output = 'test/test.exe'
    if os.path.exists('x64/Debug/CLISimpleLauncher.exe'):
        with open('x64/Debug/CLISimpleLauncher.exe', 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + shebang + archive_data.getvalue()
        with open(options.output, 'wb') as f:
            f.write(data)
        print('wrote %s' % options.output)
    if options.output == 'test/test.exe' and os.path.exists('x64/Debug/GUISimpleLauncher.exe'):
        with open('x64/Debug/GUISimpleLauncher.exe', 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + wshebang + warchive_data.getvalue()
        with open('test/testw.exe', 'wb') as f:
            f.write(data)
        print('wrote test/testw.exe')


if __name__ == '__main__':
    sys.exit(main())
