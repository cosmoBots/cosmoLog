#!/usr/bin/env python
# coding: utf-8

from datalogger import PfLog
import serial
import config

# Sends COM.x to pfeiffer
def recoverPfeiffer():
    firstTime = False
    PfLog.dre.command_tx_buf="COM,1".encode()
    PfLog.sendCtrlCommand()
    PfLog.getCtrlResponse()


# Opens serial port
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
    print("Chosen serial port: " + config.cte_serial_port)
#datalogger(serport,getDataPfeiffer,rm_cat_press1,rm_cat_press2,"press")

    PfLog.dre.ser = serport
    recoverPfeiffer()





