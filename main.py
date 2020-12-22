from ctypes import *
import socket, time
import requests

from uuid import getnode as get_mac


mac = get_mac()

h = iter(hex(mac)[2:].zfill(12))
mac2 = ":".join(i + next(h) for i in h)
print mac2
ip = socket.gethostbyname(socket.gethostname())
ip = ip[:len(ip) - 3]

for i in range(200,205):
    params = "protocol=TCP,ipaddress="+ ip + str(i) +",port=4370,timeout=1000,passwd="
    print(params)
    commpro = windll.LoadLibrary("plcommpro.dll")
    constr = create_string_buffer(params)
    hcommpro = commpro.Connect(constr)
    if(hcommpro != 0):
        print("Autoriza")
        x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
        print(x)
    print (hcommpro)



# buffer = create_string_buffer(2048)
# items = "DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime"
# p_items = create_string_buffer(items)
# ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
# print (buffer.value)

# items = "DeviceID=4,Door1SensorType=2,Door1Drivertime=6,Door1Intertime=3"
# p_items = create_string_buffer(items)
# ret = commpro.SetDeviceParam(hcommpro, p_items)

# table = "user" # Download the user data from the user table
# fieldname = "*" # Download all field information in the table
# pfilter = "" # Have no filtering conditions and thus download all information
# options = ""
# query_buf = create_string_buffer(4*1024*1024)
# query_table = create_string_buffer(table)
# query_fieldname = create_string_buffer(fieldname)
# query_filter = create_string_buffer(pfilter)
# query_options = create_string_buffer(options)
# ret = commpro.GetDeviceData(hcommpro, query_buf, 4*1024*1024, query_table, query_fieldname, query_filter, query_options)

# #mylist = query_buf.value.split(',')
# lines = query_buf.value.split('\r\n')
# del lines[0]

# for x in range(len(lines)):
#   print(lines[x])


#for i in range(lines)
 #   print (lines[i])
# table = "user" # User information table
# data = "Pin=19999\tCardNo=13375401\tPassword=1\r\nPin=2\tCardNo=14128058\tPassword=1"
# p_table = create_string_buffer(table)
# str_buf = create_string_buffer(data)
# ret = commpro.SetDeviceData(hcommpro, p_table, str_buf, "") # Upload the str_buf data


# print (ret)