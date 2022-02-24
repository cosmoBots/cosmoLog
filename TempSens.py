#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from datalogger import *
import threading
from time import sleep
from config import *

print("Doreturn inicializado")
doReturn = True

def keep_alive():
    global talive
    print("TEMP RECOVERY: ",PfLog.dre.command_tx_buf)
    PfLog.sendCtrlCommand()
    talive = threading.Timer(10.0,keep_alive)
    talive.start()
    

def doit():
    #print("doit: ", threading.get_ident())
    global doReturn
    doReturn = True

def getDataLakeshore():
    if (cte_simulate_sensors) or (cte_emulate_devices):
        #print("Espero 0.3 segundos")
        sleep(.5)
        return 99, 5555.0, 98, 5554
    else:
        global t
        global doReturn
        global talive
        while not doReturn:
            sleep(0.05)

        #print("getDataLakeshore: ", threading.get_ident())
        t = threading.Timer(cfg_temp_read_period, doit)
        t.start()
        doReturn = False
        PfLog.dre.command_tx_buf="RDGST? A".encode()
        PfLog.sendCtrlCommand()
        talive = threading.Timer(10.0,keep_alive)
        talive.start()
        #print("programo timer")
        PfLog.getCtrlResponse()
        #print("cancelo timer")
        talive.cancel()
        resp1 = PfLog.dre.command_rx_str
        status1 = int(resp1.strip())   # Removes whitespaces and assign to status of first channel
        PfLog.dre.command_tx_buf="KRDG? A".encode()
        PfLog.sendCtrlCommand()
        talive = threading.Timer(10.0,keep_alive)
        talive.start()
        #print("programo timer")
        PfLog.getCtrlResponse()
        #print("cancelo timer")
        talive.cancel()
        resp1 = PfLog.dre.command_rx_str
        value1 = float(resp1.strip())  # Removes whitespaces and assign to value of first channel
        PfLog.dre.command_tx_buf="RDGST? B".encode()
        PfLog.sendCtrlCommand()
        talive = threading.Timer(10.0,keep_alive)
        talive.start()
        #print("programo timer")
        PfLog.getCtrlResponse()
        #print("cancelo timer")
        talive.cancel()
        resp2 = PfLog.dre.command_rx_str
        status2 = int(resp2.strip())   # Removes whitespaces and assign to status of second channel
        PfLog.dre.command_tx_buf="KRDG? B".encode()
        PfLog.sendCtrlCommand()
        talive = threading.Timer(10.0,keep_alive)
        talive.start()
        #print("programo timer")
        PfLog.getCtrlResponse()
        #print("cancelo timer")
        talive.cancel()
        resp2 = PfLog.dre.command_rx_str
        value2 = float(resp2.strip())  # Removes whitespaces and assign to value of second channel

        return status1, value1, status2, value2


# In[ ]:

if not cte_emulate_devices:
    serport = serial.Serial(
            port=config.cte_serial_port2,
            baudrate=9600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
            rtscts=False,
            dsrdtr=False,
            xonxoff=True
        )
    if config.cte_verbose:
        print("Chosen serial port: " + config.cte_serial_port2)
else:
    serport = None

def execTempDatalog():
    datalogger(serport,getDataLakeshore,"Temp1","Temp2","temp",cfg_temp_nsamples_period1, cfg_temp_nsamples_period2)

tempDatalog = threading.Thread(target=execTempDatalog, name="tempDatalog")
print("*** Lanzo tempDatalog")
tempDatalog.start()
veces = 1
while(1):
    sleep(10)
    threadvivo = tempDatalog.is_alive()
    if not threadvivo:
        tempDatalog = threading.Thread(target=execTempDatalog, name="tempDatalog")
        print("*** Relanzo tempDatalog",veces)
        tempDatalog.start()


