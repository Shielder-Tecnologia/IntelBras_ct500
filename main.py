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
timeBuscaDisp = 240
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

def setData(hcommpro, lines, table):
    #for i in range(lines):
    #   print (lines[i])
    #data = "Pin=19999\tCardNo=13375401\tPassword=1\r\nPin=2\tCardNo=14128058\tPassword=1"
    p_table = create_string_buffer(table)
    str_buf = create_string_buffer(lines)
    ret = commpro.SetDeviceData(hcommpro, p_table, str_buf, "") # Upload the str_buf data
    return ret


def getData(hcommpro,table):
    #table  Download the user data from the user table
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
    #print("lista")
    #print(query_buf.value)
    lines = query_buf.value.split('\r\n')
    return lines

def deleteUser(hcommpro, user):
    table = "user"
    data = "Pin="+str(user) # Conditions of deleting the data
    p_table = create_string_buffer(table)
    p_data = create_string_buffer(data)
    ret = commpro.DeleteDeviceData(hcommpro, p_table, p_data, "")
    return ret

def connectDisp(lines):
    if(not any('=' in s for s in lines)):
        print("Nenhum dispositivo encontrado")
        timeBuscaDisp = 60
    
    for i in range(len(lines)):
        #print("linha"+ lines[x])
        
        if(len(lines[i]) > 1 and "=" in lines[i]):
            
            #print("linha"+lines[x])
            res = dict(item.split("=") for item in lines[i].split(","))
            params = "protocol=TCP,ipaddress="+ res["IP"] +",port=4370,timeout=1000,passwd="
            print("parametros"+params)
            if(not any(x for x in dispositivos if x.sn == res["SN"])):


                print("Conectando ao dispositivo"+ res["IP"])
                constr = create_string_buffer(params)
                hcommpro = commpro.Connect(constr)
                print (hcommpro)

                if(hcommpro != 0):
                    timeBuscaDisp = 360

                    url = "http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ res["SN"] +"&ip="+res["IP"]
                    idterminal = requests.get(url)
                    print("autoriza retorno "+str(idterminal.text))
                    if(int(idterminal.text)>=4):
                        #SETAR O ID DISP
                        items = "DeviceID="+str(idterminal.text)+",Door1SensorType=2,Door1Drivertime=6,Door1Intertime=3"
                        p_items = create_string_buffer(items)
                        ret = commpro.SetDeviceParam(hcommpro, p_items)
                        if(ret == 0):
                            disp = Dispositivos(res["IP"],res["SN"], str(idterminal.text), hcommpro)
                            dispositivos.append(disp)
                            print(disp.sn)
                
                # buffer = create_string_buffer(2048)
                # items = "DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime"
                # p_items = create_string_buffer(items)
                # ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
                # print (buffer.value)
                
                


                #x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ res["SN"] +"&ip="+res["IP"])
                time.sleep(2)

    for i in range(len(dispositivos)):
        if not any(dispositivos[i].sn in s for s in lines):
            print("Dispositivo desconectado "+dispositivos[i].ip)
            dispositivos.pop(i)
            print("Procurando Dispositivos novamente")
            lines = searchDevices()
            print(lines)
            #lines.append("MAC=TESTE03:18:99:C7:C2:3E,IP=192.168.0.202,SN=BBM4180048,Device=TESTE,Ver=AC Ver 4.3.4 Dec 29 2017")
            connectDisp(lines)
            

    

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def formatUser(lines):
    formattedStr = ""
    #print(lines[0])
    # lines = lines[0].split(',')
    #print("user:")
    for i in range (1, len(lines)):
        if(lines[i] is not None):
            user = lines[i].split(',')
            #print (user)
            if(len(user) > 2):    
                formattedStr += "Pin="+user[1]+"\tCardNo="+user[0]+"\tPassword="+user[2]+"\tGroup="+user[3]+"\tStartTime="+user[4]+"\tEndTime="+user[5]+"\tSuperAuthorize="+user[6]+"\r\n"
                #print(formattedStr)
    #print(formattedStr)
    return formattedStr


def formatAut(lines):
    formattedStr = ""
    #print(lines[0])
    # lines = lines[0].split(',')
    #print("user:")
    for i in range (1, len(lines)):
        if(lines[i] is not None):
            privList = lines[i].split(',')
            #print (user)
            if(len(privList) > 2):    
                formattedStr += "Pin="+privList[0]+"\tAuthorizeTimezoneId="+privList[1]+"\tAuthorizeDoorId="+privList[2]+"\r\n"
                #print(formattedStr)
    #print(formattedStr)
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
        
    if(contTimer % timeBuscaDisp == 0):
        print("Procurando Dispositivos")
        lines = searchDevices()
        print(lines)
        #lines.append("MAC=TESTE03:18:99:C7:C2:3E,IP=192.168.0.202,SN=BBM4180048,Device=TESTE,Ver=AC Ver 4.3.4 Dec 29 2017")
        connectDisp(lines)
        contTimer = 0
    #print(contTimer)
    
    #if(contTimer >= timeDispAut):

    if(retServer > 4):
        if(len(dispositivos) > 0):
            for i in range(len(dispositivos)):
                rt_log = create_string_buffer(256)
                ret = commpro.GetRTLog(dispositivos[i].hcommpro, rt_log, 256)
                print("rtlog")
                print(rt_log.value)
                res = rt_log.value.split(",")
                #print(res)
                if(res[3] == "1" and res[1]  != "0"):
                    urlCopia = "http://box.shielder.com.br/controle/getAutorizaMorador.php?mac="+ dispositivos[i].sn + "&biometria=" + res[1] + "&data=" + res[0]
                    usersCopia = requests.get(urlCopia).json()
                    print("Morador autorizado " + res[1])

            if(contTimer % timeCopiaApaga == 0):
                
                #print("Pegando usuarios")
                urlCopia = "http://box.shielder.com.br/controle/getCopiaMoradores.php?mac="+ mac2
                usersCopia = requests.get(urlCopia).json()
                
                if usersCopia is not None:
                    disp = next((disp for disp in dispositivos if disp.idDisp == usersCopia[0]['id_terminal'] ), None)

                    if(disp):
                        print("Pegando usuarios")
                        linesUser = getData(disp.hcommpro,"user")
                        linesAut = getData(disp.hcommpro,"userauthorize")

                        if(linesUser):
                            #print ("lines")
                            linesUser.append(""+usersCopia[0]['tag']+","+usersCopia[0]['id']+",,0,0,0,0")
                            users = formatUser(linesUser)
                            print("users")
                            print(users)
                            linesUser = []
                            #users = ""
                            if(users):
                                ret = setData(disp.hcommpro,users, "user")
                                #ret2 = setData(dispositivos[0].hcommpro, users, "user")
                                if(ret == 0):
                                    linesAut.append(""+usersCopia[0]['tag']+",1,1")
                                    usersAut = formatAut(linesAut)
                                    retAut = setData(disp.hcommpro,usersAut, "userauthorize")
                                    if(retAut == 0):
                                        urlCadastraBio = "http://box.shielder.com.br/controle/getCadastraBio.php?usuario=" + usersCopia[0]['id_tag'] + "&id=0"+"&mac=" + disp.sn + "&tipo=ENTRADA" + "&descricao=CARTAO"
                                        print(urlCadastraBio)
                                        retBio = requests.get(urlCadastraBio)


                #print (lines)
                    #dar append em lines com o user e dar o setDeviceData

                urlApaga = "http://box.shielder.com.br/controle/getApagaMoradores.php?mac="+ mac2
                usersApaga = requests.get(urlApaga).json()
                if usersApaga is not None:
                    disp = next((disp for disp in dispositivos if disp.idDisp == usersApaga[0]['id_terminal'] ), None)
                    if(disp):
                        ret = deleteUser(disp.hcommpro,usersApaga[0]['id'])
                        if(ret == 0):
                            lines = getData(disp.hcommpro,"user")
                            if(not any(usersApaga[0]['id'] in s for s in lines)):
                                urlCadastraBio = "http://box.shielder.com.br/controle/getCadastraBio.php?usuario=" + usersApaga[0]['id_tag'] + "&id=0"+"&mac=" + disp.sn + "&tipo=SAIDA" + "&descricao=CARTAO"
                                retBio = requests.get(urlCadastraBio)
                                print("Usuario apagado " + usersApaga[0]['id'])
                        
                        
                        




    contTimer = contTimer+1
    time.sleep(1)



