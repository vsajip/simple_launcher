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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shebang', help='Specify shebang to add')
    parser.add_argument('-o', '--output', help='Specify output filename')
    options = parser.parse_args()
    script_data = MAIN.strip().encode('utf-8')
    archive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('__main__.py', script_data)
    if options.shebang is None:
        options.shebang = '/usr/bin/env python3 -u'
    else:
        # hard to escape double quotes in command line, so replace
        # single quotes with double
        options.shebang = options.shebang.replace('\'', '"')
    shebang = ('#!%s\n' % options.shebang).encode('utf-8')
    with open('x64/Debug/CLISimpleLauncher.exe', 'rb') as f:
        launcher_data = f.read()
    data = launcher_data + shebang + archive_data.getvalue()
    if options.output is None:
        options.output = 'test/test.exe'
    with open(options.output, 'wb') as f:
        f.write(data)
    if options.output == 'test/test.exe':
        with open('x64/Debug/GUISimpleLauncher.exe', 'rb') as f:
            launcher_data = f.read()
        data = launcher_data + shebang + archive_data.getvalue()
        with open('test/testw.exe', 'wb') as f:
            f.write(data)
        



if __name__ == '__main__':
    sys.exit(main())
