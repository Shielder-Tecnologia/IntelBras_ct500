from ctypes import *
import socket, time
import requests

from uuid import getnode as get_mac
class Dispositivos:
    def __init__ (self, ip, sn, idDisp, hcommpro):
        self.sn = sn
        self.ip = ip
        self.idDisp = idDisp
        self.hcommpro = hcommpro

dispositivos = []
retServer = 0
timeServerAut = 20
timeDispAut = 10
timeBuscaDisp = 60
contTimer = 0
timeCopiaApaga = 5

mac = get_mac()
h = iter(hex(mac)[2:].zfill(12))
mac2 = ":".join(i + next(h) for i in h)
print mac2


ip = socket.gethostbyname(socket.gethostname())
#ip = ip[:len(ip) - 3]
retServer = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
 
commpro = windll.LoadLibrary("plcommpro.dll")

def setUserData(hcommpro, lines):
    #for i in range(lines):
    #   print (lines[i])
    table = "user" # User information table
    #data = "Pin=19999\tCardNo=13375401\tPassword=1\r\nPin=2\tCardNo=14128058\tPassword=1"
    p_table = create_string_buffer(table)
    str_buf = create_string_buffer(lines)
    ret = commpro.SetDeviceData(hcommpro, p_table, str_buf, "") # Upload the str_buf data
    return ret


def getUsersData(hcommpro):
    table = "user" # Download the user data from the user table
    fieldname = "*" # Download all field information in the table
    pfilter = "" # Have no filtering conditions and thus download all information
    options = ""
    query_buf = create_string_buffer(4*1024*1024)
    query_table = create_string_buffer(table)
    query_fieldname = create_string_buffer(fieldname)
    query_filter = create_string_buffer(pfilter)
    query_options = create_string_buffer(options)
    ret = commpro.GetDeviceData(hcommpro, query_buf, 4*1024*1024, query_table, query_fieldname, query_filter, query_options)

    #mylist = query_buf.value.split(',')
    print("lista")
    print(query_buf.value)
    lines = query_buf.value.split('\r\n')
    return lines

def deleteUser(hcommpro, user):
    table = "user"
    data = "Pin="+str(user) # Conditions of deleting the data
    p_table = create_string_buffer(table)
    p_data = create_string_buffer(data)
    ret = commpro.DeleteDeviceData(hcommpro, p_table, p_data, "")

def connectDisp(lines):
    for x in range(len(lines)):
        #print("linha"+ lines[x])
        
        if(len(lines[x]) > 1 and "=" in lines[x]):
            
            #print("linha"+lines[x])
            res = dict(item.split("=") for item in lines[x].split(","))
            params = "protocol=TCP,ipaddress="+ res["IP"] +",port=4370,timeout=1000,passwd="
            #print("parametros"+params)
            if(not any(x for x in dispositivos if x.sn == res["SN"])):


                print("Conectando ao dispositivo"+ res["IP"])
                constr = create_string_buffer(params)
                hcommpro = commpro.Connect(constr)
                print (hcommpro)

                if(hcommpro != 0):


                    url = "http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ res["SN"] +"&ip="+res["IP"]
                    x = requests.get(url)
                    print("autoriza retorno"+str(x.text))
                    if(int(x.text)>=4):
                        #SETAR O ID DISP
                        items = "DeviceID="+str(x)+",Door1SensorType=2,Door1Drivertime=6,Door1Intertime=3"
                        p_items = create_string_buffer(items)
                        ret = commpro.SetDeviceParam(hcommpro, p_items)
                        if(ret == 0):
                            disp = Dispositivos(res["IP"],res["SN"], str(x),hcommpro)
                            dispositivos.append(disp)
                            print(disp.sn)
                
                # buffer = create_string_buffer(2048)
                # items = "DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime"
                # p_items = create_string_buffer(items)
                # ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
                # print (buffer.value)
                
                


                #x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ res["SN"] +"&ip="+res["IP"])
                time.sleep(2)
            #x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
        
        #print(res["Device"])
def formatUser(lines):
    formattedStr = ""
    #print(lines[0])
    # lines = lines[0].split(',')
    print("user:")
    for i in range (1, len(lines)):
        if(lines[i] is not None):
            user = lines[i].split(',')
            #print (user)
            if(len(user) > 2):    
                formattedStr += "Pin="+user[1]+"\tCardNo="+user[0]+"\tPassword="+user[2]+"\r\n"
                #print(formattedStr)
    print(formattedStr)
    return formattedStr


def searchDevices():
    dev_buf = create_string_buffer("", 64*1024)
    ret=commpro.SearchDevice("UDP", "255.255.255.255", dev_buf)
    lines = dev_buf.value.split('\r\n')
    return lines
#Busca por UDP de devices na rede 

while(1):
    #AutorizaBox para o servidor
    if(contTimer % timeServerAut == 0):
        retServer = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
        contTimer = 0
    if(contTimer % timeBuscaDisp == 0):
        print("Procurando Dispositivos")
        lines = searchDevices()
        print(lines)
        connectDisp(lines)
            
    
    #if(contTimer >= timeDispAut):

    if(retServer > 4):
        if(len(dispositivos) > 0):
            rt_log = create_string_buffer(256)
            ret = commpro.GetRTLog(dispositivos[0].hcommpro, rt_log, 256)
            print("rtlog")
            print(rt_log.value)
            if(contTimer % timeCopiaApaga == 0):
            
                print("Pegando usuarios")
                #urlCopia = "http://box.shielder.com.br/controle/getCopiaMoradores.php?mac="+ mac2
                #usersCopia = requests.get(urlCopia).json()
                #if usersCopia is not None:
                lines = getUsersData(dispositivos[0].hcommpro)
                #print (lines)
                #lines.append('11,22,33,44,55,66,77')
                users = formatUser(lines)
                #print(users)
                #lines = []
                #users = ""
                #if(users):
                    #ret = setUserData(dispositivos[0].hcommpro,users)
                    #if(ret == 0):
                        #cadastrabio   


                #print (lines)
                    #dar append em lines com o user e dar o setDeviceData

                # urlApaga = "http://box.shielder.com.br/controle/getApagaMoradores.php?mac="+ mac2
                # usersApaga = requests.get(urlApaga).json()
                # if usersCopia is not None:
                #     lines = getUsersData()
                    #dar um remove com o user e dar o setDeviceData
    

    contTimer = contTimer+1
    time.sleep(1)

#Estabelece a conexao entre o servidor e os dispositivos encontrados


#x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)

#del lines[0]

# for x in range(len(lines)):
#     print(lines[x])

    
# while (1):
#     for i in range(200,205):
#         params = "protocol=TCP,ipaddress="+ ip + str(i) +",port=4370,timeout=1000,passwd="
#         print(params)
#         commpro = windll.LoadLibrary("plcommpro.dll")
#         constr = create_string_buffer(params)
#         hcommpro = commpro.Connect(constr)
#         if(hcommpro != 0):
#             print("Autoriza")
#             buffer = create_string_buffer(2048)
#             items = "DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime,SerialNumber"
#             p_items = create_string_buffer(items)
#             ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
#             print (buffer.value)
#             #x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
#             #print(x)
#         #print (hcommpro)
#     time.sleep(2)



# buffer = create_string_buffer(2048)
# items = "DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime"
# p_items = create_string_buffer(items)
# ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
# print (buffer.value)

# items = "DeviceID=4,Door1SensorType=2,Door1Drivertime=6,Door1Intertime=3"
# p_items = create_string_buffer(items)
# ret = commpro.SetDeviceParam(hcommpro, p_items)

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