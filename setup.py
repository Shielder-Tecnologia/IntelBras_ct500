import cx_Freeze
import sys
import os
import os.path

import re

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR,'tcl', 'tcl8.5')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR,'tcl', 'tk8.5')

executables = [cx_Freeze.Executable('form.py')]

cx_Freeze.setup(
    name='Email Extractor X',
    version='0.01',
    executables=executables,
    options = {"build_exe":{
    'include_files':[
        os.path.join(PYTHON_INSTALL_DIR,'DLLs','tk85.dll'),
        os.path.join(PYTHON_INSTALL_DIR,'DLLs','tcl85.dll')
    ]}}
)