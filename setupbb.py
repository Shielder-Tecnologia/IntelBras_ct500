from bbfreeze import Freezer 
import os
import os.path

includes = []
excludes = []

os.environ['TCL_LIBRARY'] = os.path.join('c:\Program Files\lib\tcl8.5','tcl', 'tcl8.5')
os.environ['TK_LIBRARY'] = os.path.join('c:\Program Files\lib\tcl8.5','tcl', 'tk8.5')


bbFreeze_Class = Freezer('distForm',includes=includes, excludes=excludes)

bbFreeze_Class.addScript("form.py",gui_only=True)

bbFreeze_Class.use_compression = 0
bbFreeze_Class.include_py = True
bbFreeze_Class()