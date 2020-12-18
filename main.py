import ctypes



params = b"protocol=TCP,ipaddress=192.168.0.201,port=4370,timeout=4000,passwd="
commpro = ctypes.windll.LoadLibrary("plcommpro.dll")
constr = ctypes.create_string_buffer(params)
hcommpro = commpro.Connect(constr)

print (hcommpro)