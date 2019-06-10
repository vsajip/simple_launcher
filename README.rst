What is it?
===========
This is a simple launcher for script files under Windows, originally
developed for use with Python scripts, though nothing in it is Python-
specific. There are two versions of the launcher - console and GUI -
built from the same source code.

The launcher is intended to facilitate script execution under Windows by
processing shebang lines in an analogous way to how shebang lines are
processed on POSIX platforms.

How does it work?
=================
The launcher relies on script executors which can process scripts which
are contained in .zip archives. Python, for example, can do this. The
launcher is used to make a native Windows executable file - .exe - which
is constructed by concatenating the launcher, a shebang line and a .zip
archive which contains the script to execute. When the executable is run,
code in the launcher gets control. It knows how to find the shebang line
which is concatenated to it, which is expected to be decodable using the
UTF-8 encoding. The shebang is processed to find the executable and
any arguments in it. A command line is constructed using the found
executable, the arguments, and the pathname to the source executable. A
child processs is created to execute this command line, and once it
exits, the launcher does, too.

An example
==========
An example with Python: consider a script foo.py which needs to be run as
a native executable. The corresponding foo.exe will contain the
concatenation of, in order, the following:

1. A launcher "stub" which depends on the platform - whether a console or
   windowed application is wanted, and whether it's 32-bit or 64-bit. So
   there are four possible launchers stubs, usually deployed as t32.exe,
   t64.exe, w32.exe and w64.exe.
2. A POSIX-format shebang line which is terminated with a newline. This
   must be UTF-8 encoded.
3. A .zip archive containing foo.py, in the format for ZIP archives
   required by a script executor such as a Python interpreter, such that
   "python foo.zip" would execute the script foo.py in the same way as
   "python foo.py". See `PEP 273
   <https://www.python.org/dev/peps/pep-0273/>`_ for how Python runs
   .zip archives.

The shebang line will be of the form::

    #!<executable-definition> <arguments> <newline>

The *executable-definition* can be an absolute or relative path, or have
the special form ``/usr/bin/env program-name``, which causes
``program-name`` to be searched for in the Windows PATH. If a relative or
absolute path is used, then it will use standard pathname syntax, quoted
with double quotes if it contains spaces. If the path starts with the
literal string "<launcher_dir>\", then the directory of foo.exe is used
to replace "<launcher_dir>". The resulting path (quoted if it has spaces)
is then used to construct a command line. For example, the shebang line::

    #!/usr/bin/env python -u

in ``foo.exe`` might be converted to::

    c:\Python37\python.exe -u foo.exe

and this command line is used to initialise a child process. When Python
runs, it sees that foo.exe is actually a .zip archive, and executes it,
ignoring the launcher stub and shebang which precede the .zip archive in
foo.exe.
