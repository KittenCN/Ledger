"""
PyInstaller runtime hook: fix _ctypes DLL loading on Python 3.8+ / Windows.

Python 3.8+ on Windows introduced a stricter DLL search policy that no longer
automatically searches the process working directory.  When running a frozen
PyInstaller bundle the _internal/ folder (sys._MEIPASS) is NOT on the default
search path, so _ctypes.pyd cannot find libffi-7.dll (or similar) at import
time.  os.add_dll_directory() explicitly whitelists a directory so that any DLL
placed there is discoverable by the loader.
"""
import os
import sys

if hasattr(os, "add_dll_directory") and hasattr(sys, "_MEIPASS"):
    # _internal/ directory – contains _ctypes.pyd and libffi-*.dll
    os.add_dll_directory(sys._MEIPASS)

    # exe directory (parent of _internal/) – some DLLs land here
    exe_dir = os.path.dirname(sys.executable)
    if os.path.isdir(exe_dir):
        os.add_dll_directory(exe_dir)
