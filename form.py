from ctypes import *
from tkinter import *
import socket, time
import win32gui, win32con
from tkinter import ttk
import sys
import os
import os.path

import re



os.environ['TCL_LIBRARY'] = os.path.join('c:\Program Files\lib\\tcl8.5')
os.environ['TK_LIBRARY'] = os.path.join('c:\Program Files\lib\\tcl8.5')




class Dispositivos:
    def __init__ (self, ip, mac):
        self.mac = mac
        self.ip = ip


listIps = []


ip = socket.gethostbyname(socket.gethostname())
commpro = windll.LoadLibrary("plcommpro.dll")
def set_ip():
    #print (macDisp)
    #mac = txt_user # MAC address of the target device
    new_ip = txt_ipnew.get() # New IP address of the device
    gateway = txt_gateway.get()
    disp = next((disp for disp in listIps if disp.ip == cb_ips.get() ), None)
    #comm_pwd = ""
    str = "MAC=%s,IPAddress=%s,GATEIPAddress=%s " % (disp.mac ,new_ip,gateway)
    #print(str)
    p_buf = create_string_buffer(str)
    modify_ip = commpro.ModifyIPAddress("UDP", "255.255.255.255", p_buf)
    if(modify_ip>=0):
        result.set("IP Setado")
        #app.destroy()
    else:
        result.set("Erro ao setar ip "+ modify_ip.__str__())
def connectDisp(lines):
    if(not any('=' in s for s in lines)):
        #print("Nenhum dispositivo encontrado")
        result.set("Nenhum dispositivo encontrado")
        #timeBuscaDisp = 60
    else:
        result.set("Dispositivo encontrado!")
    for i in range(len(lines)):
        if(len(lines[i]) > 1 and "=" in lines[i]):
        
            # print("linha"+lines[x])
            res = dict(item.split("=") for item in lines[i].split(","))

            spltDisp = res["IP"].split(".")
            subdomainDisp = spltDisp[0]+"."+spltDisp[1]+"."+spltDisp[2]

            spltServer = ip.split(".")
            subdomainServer = spltServer[0]+"."+spltServer[1]+"."+spltServer[2]

            disp = Dispositivos(res["IP"],res["MAC"])
            listIps.append(disp)
            
            disp2 = Dispositivos("111.222.333.444","09:22:12:E3:3D")
            listIps.append(disp2)
            ipList = []
            for item in listIps:
                ipList.append(item.ip)

            cb_ips['values'] = ipList
            cb_ips.set(ipList[0])

            #print(res["MAC"])
            #macDisp.set(res["MAC"])
            #print (macDisp)
            #ipOldVar.set(res["IP"])
            app.lift()
            ipNewVar.set(subdomainServer)
            gatewayVar.set(subdomainServer)


def searchDevices():
    dev_buf = create_string_buffer("", 64*1024)
    ret=commpro.SearchDevice("UDP", "255.255.255.255", dev_buf)
    lines = dev_buf.value.split('\r\n')
    #print (lines)
    connectDisp(lines)

app = Tk()
#Form
#app.geometry("400x150")
app.resizable(False, False)
app.title("Configurar IP")

#LabelIPOld
lblIpAntigo = Label(app, text = "IP Antigo: ").grid(row=0,sticky = W)

#LabelResult]
result = StringVar()
lblResult = Label(app, textvariable = result).grid(row=4,sticky = W)

macDisp = StringVar()
lblMac = Label(app, textvariable = macDisp)
lblMac.grid(row=1, column = 1,sticky = W)
#LabelIPNew
lblIpNovo = Label(app, text = "IP novo: ").grid(row=1,sticky = W)


#LabelGateway
lblIpGateway = Label(app, text = "Gateway: ").grid(row=2,sticky = W)


#txtipOld
ipOldVar = StringVar(None)

cb_ips = ttk.Combobox(app, textvariable = ipOldVar )
cb_ips.grid(row=0,column=1, sticky = W)
#txt_ipold = Entry(app, textvariable = ipOldVar)
#txt_ipold.grid(row=0,column=1, sticky = W)
#txtipNew
ipNewVar = StringVar(None)
txt_ipnew = Entry(app, textvariable = ipNewVar)
txt_ipnew.grid(row=1,column=1, sticky = W)
#txtipGateway
gatewayVar = StringVar(None)
txt_gateway = Entry(app, textvariable = gatewayVar)
txt_gateway.grid(row=2,column=1, sticky = W)


#buttonSet
btnSet = Button(app, text = "Setar IP", command = set_ip).grid(row=3, column=1,sticky = SE)

#buttonSearch
btnSearch = Button(app, text = "Procurar IP", command = searchDevices).grid(row=3, column=0,sticky = SE)
#btn.pack()

            


#app.lift()
#searchDevices()
app.lift()
app.mainloop()