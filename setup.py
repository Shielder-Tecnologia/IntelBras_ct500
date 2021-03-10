from bbfreeze import Freezer 

includes = []
excludes = []

bbFreeze_Class = Freezer('dist',includes=includes, excludes=excludes)

bbFreeze_Class.addScript("main.py",gui_only=True)

bbFreeze_Class.use_compression = 0
bbFreeze_Class.include_py = True
bbFreeze_Class()