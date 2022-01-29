@echo off
python3 update_build.py
"C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\devenv.exe" SimpleLauncher.sln /build "Debug|Win32" /out build.log
"C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\devenv.exe" SimpleLauncher.sln /build "Release|Win32" /out build.log
"C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\devenv.exe" SimpleLauncher.sln /build "Debug|x64" /out build.log
"C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\devenv.exe" SimpleLauncher.sln /build "Release|x64" /out build.log
