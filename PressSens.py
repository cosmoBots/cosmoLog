#!/usr/bin/env python
# coding: utf-8

from datalogger import *
import threading
from time import sleep
from config import *

talive = None

def keep_alive():
    global talive
    PfLog.dre.command_tx_buf="COM,1".encode()    
    print("PRESS RECOVERY: ",PfLog.dre.command_tx_buf)
    PfLog.sendCtrlCommand()
    #print("programo timer")
    talive = threading.Timer(10.0,keep_alive)
    talive.start()

# Gets a response from the Motors
def getDataPfeiffer():
    if (cte_simulate_sensors):
        #print("Espero 0.3 segundos")
        sleep(.5)
        return 99, 5555.0, 98, 5554
    else:    
        global talive
        done = False
        while not done:
            #print("programo timer")
            talive = threading.Timer(10.0,keep_alive)
            talive.start()
            PfLog.getCtrlResponse()
            talive.cancel()
            # PfLog.dre.command_rx_buf
            resp2 = PfLog.dre.command_rx_str
            splitresp = resp2.split(',')  # Splits the string into groups
            done = (len(splitresp)>=4)
            if not done:
                print("SKIPPING UNKNOWN MSG: ",resp2)


        status1 = int(splitresp[0].strip())  # Removes whitespaces and assign to status of first channel
        value1 = float(splitresp[1].strip()) * 1e9  # Removes whitespaces and assign to value of first channel
        status2 = int(splitresp[2].strip())  # Removes whitespaces and assign to status of second channel
        value2 = float(splitresp[3].strip()) * 1e9  # Removes whitespaces and assign to value of second channel

        return status1, value1, status2, value2


# In[ ]:


serport = serial.Serial(
        port=config.cte_serial_port,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        rtscts=False,
        dsrdtr=False,
        xonxoff=True
    )
if config.cte_verbose:
    print("PRESS serial port: " + config.cte_serial_port)
    

def execPressDatalog():
    datalogger(serport,getDataPfeiffer,rm_cat_press1,rm_cat_press2,"press",cfg_press_nsamples_period1, cfg_press_nsamples_period2)

pressDatalog = threading.Thread(target=execPressDatalog, name="pressDatalog")
print("*** Lanzo pressDatalog")
pressDatalog.start()
veces = 1
while(1):
    sleep(10)
    threadvivo = pressDatalog.is_alive()
    if not threadvivo:
        pressDatalog = threading.Thread(target=execPressDatalog, name="pressDatalog")
        print("*** Relanzo pressDatalog",veces)
        pressDatalog.start()

