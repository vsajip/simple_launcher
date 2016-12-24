# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Vinay Sajip.
#
import io
import os
import sys
import zipfile

MAIN = '''
import sys
print(sys.version)
print(sys.argv)
'''

def main():
    script_data = MAIN.strip().encode('utf-8')
    archive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('__main__.py', script_data)
    shebang = b'#!/usr/bin/env python3\n'
    # shebang = b'#!python.exe\n'
    with open('x64/Debug/CLISimpleLauncher.exe', 'rb') as f:
        launcher_data = f.read()
    data = launcher_data + shebang + archive_data.getvalue()
    with open('test/test.exe', 'wb') as f:
        f.write(data)



if __name__ == '__main__':
    sys.exit(main())
