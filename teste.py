import sys
import os
import os.path

import re



os.environ['TCL_LIBRARY'] = os.path.join('c:\Program Files\lib\\tcl8.5')
os.environ['TK_LIBRARY'] = os.path.join('c:\Program Files\lib\\tcl8.5')

PYTHON_INSTALL_DIR = os.environ['TCL_LIBRARY']

print(PYTHON_INSTALL_DIR)