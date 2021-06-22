from ctypes import *
#import ctypes
import socket, time
import requests
import win32gui, win32con
from tkinter import *
import sys, os, shutil
import requests

#hide = ctypes.windll.kernel32.GetConsoleWindow()
#win32gui.ShowWindow(hide , win32con.SW_HIDE)

from uuid import getnode as get_mac

pathDocs = os.path.expanduser('~\Documents\ct500_log.txt')
dispositivos = []
retServer = 0
timeServerAut = 9
timeDispAut = 9
timeBuscaDisp = 120
contTimer = 0
timeCopiaApaga = 3
mac = get_mac()
h = iter(hex(mac)[2:].zfill(12))
mac2 = ":".join(i + next(h) for i in h)
mac2 = mac2 + "CT500"

with open(pathDocs, "rb") as a_file:
    file_dict = {"log": a_file}

    url = 'http://box.shielder.com.br/log/box/log.php?mac='+mac2
    x = requests.post(url, files=file_dict)
    print("Log enviado com sucesso ")


orig_stdout = sys.stdout
f = open(pathDocs, 'w')
sys.stdout = f
text = '' 
print(text)
sys.stdout = orig_stdout
f.close()

ip = socket.gethostbyname(socket.gethostname())
commpro = windll.LoadLibrary("plcommpro.dll")

class Dispositivos:
    def __init__ (self, ip, sn, idDisp, hcommpro):
        self.sn = sn
        self.ip = ip
        self.idDisp = idDisp
        self.hcommpro = hcommpro

    #printAndWrite()
def printAndWrite(text):
    print(text)
    orig_stdout = sys.stdout
    f = open(pathDocs, 'a')
    sys.stdout = f
    text = text 
    print(text)
    sys.stdout = orig_stdout
    f.close()
    


    
printAndWrite(mac2)





def connectDisp(lines):
    global timeBuscaDisp

    if(not any('=' in s for s in lines)):
        printAndWrite("Nenhum dispositivo encontrado")
        timeBuscaDisp = 15
    
    for i in range(len(lines)):
        #printAndWrite("linha"+ lines[x])
        
        if(len(lines[i]) > 1 and "=" in lines[i]):
            
           # printAndWrite("linha"+lines[x])
            res = dict(item.split("=") for item in lines[i].split(","))

            # spltDisp = res["IP"].split(".")
            # subdomainDisp = spltDisp[0]+"."+spltDisp[1]+"."+spltDisp[2]

            # spltServer = ip.split(".")
            # subdomainServer = spltServer[0]+"."+spltServer[1]+"."+spltServer[2]

            # if(subdomainServer != subdomainDisp):
            #     #printAndWrite(res["MAC"])
            #     macDisp.set( res["MAC"])
            #     #printAndWrite (macDisp)
            #     ipantigo.set(res["IP"])
            #     ipNewVar.set(subdomainServer)
            #     gatewayVar.set(subdomainServer)
                
            #     app.lift()
            #     app.mainloop()
            #     #app.mainloop()
            #     params = "protocol=TCP,ipaddress="+ txt_ipnew.get()+",port=4370,timeout=2000,passwd="
            # else:
            #     params = "protocol=TCP,ipaddress="+ res["IP"] +",port=4370,timeout=2000,passwd="
            params = "protocol=TCP,ipaddress="+ res["IP"] +",port=4370,timeout=2000,passwd="
            

            
            printAndWrite("parametros"+params)
            if(not any(x for x in dispositivos if x.sn == res["SN"])):


                printAndWrite("Conectando ao dispositivo "+ res["IP"])
                constr = create_string_buffer(params)
                hcommpro = commpro.Connect(constr)
                printAndWrite (hcommpro)

                if(hcommpro != 0):
                    timeBuscaDisp = 140

                    url = "http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ res["SN"] +"&ip="+res["IP"]
                    idterminal = requests.get(url)
                    printAndWrite("autoriza retorno "+idterminal.text)
                    if(int(idterminal.text)>=4):
                        #SETAR O ID DISP
                        items = "DeviceID="+idterminal.text+",Door1SensorType=2,Door1Drivertime=6,Door1Intertime=3"
                        p_items = create_string_buffer(items)
                        ret = commpro.SetDeviceParam(hcommpro, p_items)
                        if(ret == 0):
                            disp = Dispositivos(res["IP"],res["SN"], idterminal.text, hcommpro)
                            dispositivos.append(disp)
                            printAndWrite(disp.sn)
                        else:
                            printAndWrite("Nao foi possivel conseguir os dados do dispositivo")
                            timeBuscaDisp = 10
                else:
                    timeBuscaDisp = 10
                # buffer = create_string_buffer(2048)
                # items = "DeviceID,Door1SensorType,Door1Drivertime,Door1Intertime"
                # p_items = create_string_buffer(items)
                # ret=commpro.GetDeviceParam(hcommpro, buffer, 256, p_items)
                # printAndWrite (buffer.value)
                
                


                #x = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ res["SN"] +"&ip="+res["IP"])
                time.sleep(2)

    for i in range(len(dispositivos)):
        if not any(dispositivos[i].sn in s for s in lines):
            printAndWrite("Dispositivo desconectado "+dispositivos[i].ip)
            dispositivos.pop(i)
            printAndWrite("Procurando Dispositivos novamente")
            searchDevices()

def searchDevices():
    dev_buf = create_string_buffer("", 64*1024)
    ret=commpro.SearchDevice("UDP", "255.255.255.255", dev_buf)
    lines = dev_buf.value.split('\r\n')
    printAndWrite (lines)
    connectDisp(lines)
    #return lines    
#app.mainloop()

#ip = ip[:len(ip) - 3]
ret = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
retServer = int(ret.text)


def setData(hcommpro, lines, table):
    #for i in range(lines):
    #   printAndWrite (lines[i])
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
    #printAndWrite("lista")
    #printAndWrite(query_buf.value)
    lines = query_buf.value.split('\r\n')
    return lines

def deleteUser(hcommpro, user):
    table = "user"
    data = "Pin="+user.__str__() # Conditions of deleting the data
    p_table = create_string_buffer(table)
    p_data = create_string_buffer(data)
    ret = commpro.DeleteDeviceData(hcommpro, p_table, p_data, "")
    return ret


            

    

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def formatUser(lines):
    formattedStr = ""
    #printAndWrite(lines[0])
    # lines = lines[0].split(',')
    #printAndWrite("user:")
    for i in range (1, len(lines)):
        if(lines[i] is not None):
            user = lines[i].split(',')
            #printAndWrite (user)
            if(len(user) > 2):    
                formattedStr += "Pin="+user[1]+"\tCardNo="+user[0]+"\tPassword="+user[2]+"\tGroup="+user[3]+"\tStartTime="+user[4]+"\tEndTime="+user[5]+"\tSuperAuthorize="+user[6]+"\r\n"
                #printAndWrite(formattedStr)
    #printAndWrite(formattedStr)
    return formattedStr


def formatAut(lines):
    formattedStr = ""
    #printAndWrite(lines[0])
    # lines = lines[0].split(',')
    #printAndWrite("user:")
    for i in range (1, len(lines)):
        if(lines[i] is not None):
            privList = lines[i].split(',')
            #printAndWrite (user)
            if(len(privList) > 2):    
                formattedStr += "Pin="+privList[0]+"\tAuthorizeTimezoneId="+privList[1]+"\tAuthorizeDoorId="+privList[2]+"\r\n"
                #printAndWrite(formattedStr)
    #printAndWrite(formattedStr)
    return formattedStr



#Busca por UDP de devices na rede 




while(1):
    try:
        #AutorizaBox para o servidor
        if(contTimer % timeServerAut == 0):
            printAndWrite("AutorizaBox Servidor")
            ret = requests.get("http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ mac2 +"&ip="+ip)
            retServer = int(ret.text)
            
        if(retServer == 3):
            pathOld = "C:\Program Files (x86)\Shielder Tecnologia\Servidor CT500 Shielder\.old"
            pathSource = "C:\Program Files (x86)\Shielder Tecnologia\Servidor CT500 Shielder\library.zip"
            pathDest = "C:\Program Files (x86)\Shielder Tecnologia\Servidor CT500 Shielder\.old\library.zip"
            try:
                if(os.path.exists(pathOld)):
                    shutil.rmtree(pathOld)
                os.mkdir(pathOld)
                shutil.move(pathSource, pathDest)
                url = 'http://box.shielder.com.br/integracao/library.zip'
                r = requests.get(url)
                with open("C:\Program Files (x86)\Shielder Tecnologia\Servidor CT500 Shielder\library.zip", 'wb') as f:
                    f.write(r.content)
                    #f.write(datatowrite)


                #os.replace(pathSource, pathDest)

            except OSError:
                printAndWrite("Erro ao atualizar o programa")
            else:
                printAndWrite("Programa atualizado com sucesso")
                sys.exit("Programa sera reinicializado")
                

        if(retServer == 2):
            contTimer = contTimer+1
            time.sleep(1)   
            printAndWrite("Servidor nao cadastrado")
            break
    except:
        printAndWrite("Erro no autorizaBox")
        sys.exit(1)
    if(contTimer % timeBuscaDisp == 0):
        printAndWrite("Procurando Dispositivos")
        searchDevices()
        contTimer = 0
        #printAndWrite(contTimer)
        
        #if(contTimer >= timeDispAut):

    if(retServer > 4):
        if(len(dispositivos) > 0):
            try:
                printAndWrite("AutorizaBox Dispositivo")
                for i in range(len(dispositivos)):
                    url = "http://box.shielder.com.br/controle/getAutorizaBox.php?mac="+ dispositivos[i].sn +"&ip="+dispositivos[i].ip
                    requests.get(url)
            except:
                printAndWrite("Erro no autorizabox")

            
            for i in range(len(dispositivos)):
                rt_log = create_string_buffer(256)
                ret = commpro.GetRTLog(dispositivos[i].hcommpro, rt_log, 256)
                printAndWrite("rtlog")
                printAndWrite(rt_log.value)
                res = rt_log.value.split(",")
                #printAndWrite(res)
                if(len(rt_log.value) > 10):
                    if(res[3] == "1" and res[1]  != "0"):
                        urlAut = "http://box.shielder.com.br/controle/getAutorizaMorador.php?mac="+ dispositivos[i].sn + "&biometria=" + res[1] + "&data=" + res[0]
                        printAndWrite("Morador autorizado " + res[1])
                        usersCopia = requests.get(urlAut).json()
            


            if(contTimer % timeCopiaApaga == 0):
                try: 
                    printAndWrite("Copia")
                    urlCopia = "http://box.shielder.com.br/controle/getCopiaMoradores.php?mac="+ mac2
                    usersCopia = requests.get(urlCopia).json()
                    
                    if usersCopia is not None:
                        disp = next((disp for disp in dispositivos if disp.idDisp == usersCopia[0]['id_terminal'] ), None)

                        if(disp):
                            printAndWrite("Pegando usuarios")
                            linesUser = getData(disp.hcommpro,"user")
                            linesAut = getData(disp.hcommpro,"userauthorize")

                            if(linesUser):
                                #printAndWrite ("lines")
                                linesUser.append(""+usersCopia[0]['tag']+","+usersCopia[0]['id']+",,0,0,0,0")
                                users = formatUser(linesUser)
                                printAndWrite("users")
                                printAndWrite(users)
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
                                            printAndWrite(urlCadastraBio)
                                            retBio = requests.get(urlCadastraBio)
                    else:
                        printAndWrite("Copia Vazio")

                    #printAndWrite (lines)
                        #dar append em lines com o user e dar o setDeviceData
                except:
                    printAndWrite("Erro no copiamoradores")

                try:
                    printAndWrite("Apaga")
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
                                    printAndWrite("Usuario apagado " + usersApaga[0]['id'])

                except:
                    printAndWrite("Erro no apagamoradores")
                        
                        
                            




    contTimer = contTimer+1
    #printAndWrite("Timer: " + str(contTimer))
    time.sleep(3)
    


