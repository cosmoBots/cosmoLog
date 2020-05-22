#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from datalogger import *
import threading
from time import sleep

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

# Gets a response from the Motors
def getDataLakeshore():
    global t
    global doReturn
    global talive
    while not doReturn:
        sleep(0.05)
 
    #print("getDataLakeshore: ", threading.get_ident())
    t = threading.Timer(1.0, doit)
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
datalogger(serport,getDataLakeshore,rm_cat_temp1,rm_cat_temp2,"temp")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




