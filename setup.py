from bbfreeze import Freezer


includes = []
excludes = ['Tkinter']

bbFreeze_Class = Freezer('dist',includes=includes, excludes=excludes)

bbFreeze_Class.addScript('main.py',gui_only=False)

bbFreeze_Class.use_compression = 0
bbFreeze_Class.include_py = True
bbFreeze_Class()