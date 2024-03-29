import sys
import config
import serial
import config_tb
import requests
import time
from datetime import datetime
from collections import OrderedDict
from pyexcel_ods import save_data
import statistics
import threading
from collections import deque

sys.path.insert(0, './fsm')
import PfLog

datos_acumulados = deque([])
tupload = None

def uploader():
    global datos_acumulados
    global tupload
    
    tupload = threading.Timer(40.0,uploader)
    tupload.start()
    print("************* Datos en cola*******",len(datos_acumulados))

    while (len(datos_acumulados)>0):
        print("************* Datos en cola*******",len(datos_acumulados))
        datoasubir = datos_acumulados[0]
        if datoasubir is not None:
            print(f'Working on {datoasubir}')
            print(config_tb.telemetry_address)
            client_ts = datoasubir['tstamp']
            d = datetime.strptime(client_ts, "%Y-%m-%d %H:%M:%S")
            unixtime = int(time.mktime(d.timetuple())*1000)
            category = datoasubir['category']
            pload = {'ts':unixtime, "values":{category+'_value':datoasubir['value'],
                                              category+'_category':datoasubir['category'],
                                              category+'_minstatus':datoasubir['minstatus'],
                                              category+'_maxstatus':datoasubir['maxstatus'],   
                                              category+'_min':datoasubir['min'],
                                              category+'_max':datoasubir['max'],
                                              category+'_mean':datoasubir['mean'],
                                              category+'_median':datoasubir['median'],
                                              category+'_samples':datoasubir['samples'],
                                              category+'_tstamp':client_ts}}
            print(pload)
            print("========")
            r = requests.post(config_tb.telemetry_address,json = pload)
            print(r)
            
            datos_acumulados.popleft()
            print(f'Finished {datoasubir}')


uploaderThread = None
                
def datalogger(ser,getdata_cb,catsens1,catsens2,sensabbrev,nsamples_period1,nsamples_period2):
    global uploaderThread
    global datos_acumulados
    global tupload
    
    tupload = threading.Timer(40.0,uploader)
    tupload.start()
    
    # turn-on the worker thread
    dre = PfLog.dre

    # This is to allow consecutive partial executions of the notebook
    if False:
        if dre is not None:
            if dre.ser is not None:
                dre.ser.close()

    dre.ser = ser
    write_files = False
    write_server = True

    # Configuration
    period1 = nsamples_period1   # The number of samples per row for period 1, this period is also uploaded to server
    period2 = nsamples_period2  # The number of samples per row for period 2, this period is NOT uploaded to server
    period1_max_rows = 2880 # The maximum number of rows per file of the period 1
    period2_max_rows = 144 # The maximum number of rows per file of the period 2
    valid_status_limit = 255  # maximum status code to store values in rows.  
                # If the status is greater than this maximum, the sample will not be added to the series
                # if the full set is invalid, it will not be uploaded to server, and it will be stored
                # as "invalid" in the files

    # Initialization of counter and vectors for storage of samples
    i1 = 1
    i2 = 1
    i = 1
    period1_status1 = []
    period2_status1 = []
    period1_data1 = []
    period2_data1 = []
    period1_status2 = []
    period2_status2 = []
    period1_data2 = []
    period2_data2 = []

    # Initialization for the row counters and spreadsheet preparation
    i1_row = 1
    i2_row = 1
    sheet_data1 = OrderedDict() # from collections import OrderedDict
    sheet_data2 = OrderedDict() # from collections import OrderedDict
    px_header = ["tstamp", "min st1", "max st1", "min v1", "max v1", "mean v1", "median v1" "current v1", "min st2", "max st2", "min v2", "max v2", "mean v2", "median v2", "current v2"]
    p1_sheet_data = [px_header]
    p2_sheet_data = [px_header]
    p1_row_data = []
    p2_row_data = []

    # Begin the endless loop which acquires from the device, processes, uploads and stores
    #while (i <= 100):
    if not config.cte_emulate_devices:    
        dre.ser.flushInput()
        dre.ser.flushOutput()

    while (True):
        i += 1
        status1,value1,status2,value2 = getdata_cb()  # Gets the data from the device

        # Appending the two read statuses to the vectors we use for storing 
        # them during the series acqusition of the two periods
        period1_status1.append(status1)
        period2_status1.append(status1)
        period1_status2.append(status2)
        period2_status2.append(status2)
        # If the status is not ok, we will not add the sample to the series
        # we will consider it as invalid
        # Otherwise, we add the samples to the series for the two periods
        if (status1 < valid_status_limit):
            period1_data1.append(value1)
            period2_data1.append(value1)

        # If the status is not ok, we will not add the sample to the series
        # we will consider it as invalid
        # Otherwise, we add the samples to the series for the two periods
        if (status2 < valid_status_limit):
            period1_data2.append(value2)
            period2_data2.append(value2)

        # Print the sample to the screen, to know everything is working
        if config.cte_verbose:
            print(sensabbrev," | ",i1,": ",status1," ",value1," ",status2," ",value2)

        # If the sample was the last of the series of the period 1, we have to create a record
        # to later upload to server or store in spreadsheet row
        if (i1 >= period1):
            # The current sample is the last one
            # let's create a timestamp and add it to the record
            tstamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            p1_row_data = [tstamp]

            ##### First sensor handling
            # Let's add the min and max values of the status, to know if during the 
            # series we received errors
            p1_row_data += [min(period1_status1),max(period1_status1)]

            # If we obtained at least one valid data, we will make statistics and append the resulting
            # data to the record
            if (len(period1_data1) > 0):
                p1_row_data += [min(period1_data1),max(period1_data1),statistics.mean(period1_data1),statistics.median(period1_data1),period1_data1[-1]]
                # The record must be uploaded to the server only if there is at least one valid sample in the series
                if (write_server):
                    datoasubir = { 
                                  'subject': 'p1',
                                  'category': catsens1,
                                  'value': p1_row_data[7],
                                  'minstatus': p1_row_data[1],
                                  'maxstatus': p1_row_data[2],
                                  'min': p1_row_data[3],
                                  'max': p1_row_data[4],
                                  'mean': p1_row_data[5],
                                  'median': p1_row_data[6],
                                  'samples': len(period1_data1),
                                  'tstamp': p1_row_data[0]
                                 }
                    datos_acumulados.append(datoasubir)
                    print("Long datosacumulados",len(datos_acumulados))

            # When there is no valid data, we will add a row in the spreadsheet telling 
            # it is invalid, but we will not upload info to the server
            else:
                p1_row_data += ["Invalid","Invalid","Invalid","Invalid","Invalid"]

            if config.cte_verbose:
                print(sensabbrev," period1 tstamp: ",p1_row_data[0])
                print(sensabbrev," period1 min status1: ",p1_row_data[1])
                print(sensabbrev," period1 max status1: ",p1_row_data[2])
                print(sensabbrev," period1 min value1: ",p1_row_data[3])
                print(sensabbrev," period1 max value1: ",p1_row_data[4])
                print(sensabbrev," period1 mean value1: ",p1_row_data[5])            
                print(sensabbrev," period1 median value1: ",p1_row_data[6])            
                print(sensabbrev," period1 current value1: ",p1_row_data[7])

            ##### Second sensor handling
            # Let's add the min and max values of the status, to know if during the 
            # series we received errors
            p1_row_data += [min(period1_status2),max(period1_status2)]

            # If we obtained at least one valid data, we will make statistics and append the resulting
            # data to the record
            if (len(period1_data2) > 0):
                p1_row_data += [min(period1_data2),max(period1_data2),statistics.mean(period1_data2),statistics.median(period1_data2),period1_data2[-1]]
                # The record must be uploaded to the server only if there is at least one valid sample in the series
                if (write_server):
                    datoasubir = {
                                  'subject': 'p2',
                                  'category': catsens2,
                                  'value': p1_row_data[14],
                                  'minstatus': p1_row_data[8],
                                  'maxstatus': p1_row_data[9],
                                  'min': p1_row_data[10],
                                  'max': p1_row_data[11],
                                  'mean': p1_row_data[12],
                                  'median': p1_row_data[13],
                                  'samples': len(period1_data2),
                                  'tstamp': p1_row_data[0]
                                 }
                    datos_acumulados.append(datoasubir)                                  
                    print("Long datosacumulados",len(datos_acumulados))
                    
            # When there is no valid data, we will add a row in the spreadsheet telling 
            # it is invalid, but we will not upload info to the server
            else:
                p1_row_data += ["Invalid","Invalid","Invalid","Invalid","Invalid"]

            if config.cte_verbose:
                print(sensabbrev," period1 min status2: ",p1_row_data[8])
                print(sensabbrev," period1 max status2: ",p1_row_data[9])
                print(sensabbrev," period1 min value2: ",p1_row_data[10])
                print(sensabbrev," period1 max value2: ",p1_row_data[11])
                print(sensabbrev," period1 mean value2: ",p1_row_data[12])
                print(sensabbrev," period1 median value2: ",p1_row_data[13])
                print(sensabbrev," period1 current value2: ",p1_row_data[14])

            # Append the new record as a row in the spreadsheet
            p1_sheet_data += [p1_row_data]

            # print(p1_sheet_data)

            # In the case we have arrived to the maximum number of rows in the spreadsheet
            # we have to save it to disk, and empty the sheet data (preparing a new spreadsheet)
            if (i1_row >= period1_max_rows):
                # Store the current spreadsheet
                sheet_data1.update({"Data": p1_sheet_data})
                dt_string = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                if config.cte_verbose:
                    print("Closing period1 (current) file with tstamp " + dt_string)
                save_data(sensabbrev+"_p1_"+dt_string+".ods", sheet_data1)

                # Prepare the new spreadsheet
                sheet_data1 = OrderedDict()
                p1_sheet_data = [px_header]
                i1_row = 1
                if config.cte_verbose:
                    print("Opening period1 (new) file")

            else:
                # If the file can have more rows, we simply increase the counter of rows
                i1_row = i1_row + 1

            # As we have finished with the series, we restart the series counter
            # and empty the storage vectors
            i1 = 1
            period1_status1 = []
            period1_data1 = []
            period1_status2 = []
            period1_data2 = []

        else:
            # In the case it was not the last sample of the serie
            # We will increase the counter of samples
            i1 = i1 + 1


        # If the sample was the last of the series of the period 2, we have to create a record
        # to later upload to server or store in spreadsheet row
        if (i2 >= period2):
            # The current sample is the last one
            # let's create a timestamp and add it to the record
            tstamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            p2_row_data = [tstamp]

            ##### First sensor handling
            # Let's add the min and max values of the status, to know if during the 
            # series we received errors
            p2_row_data += [min(period2_status1),max(period2_status1)]

            # If we obtained at least one valid data, we will make statistics and append the resulting
            # data to the record
            if (len(period2_data1) > 0):
                p2_row_data += [min(period2_data1),max(period2_data1),statistics.mean(period2_data1),statistics.median(period2_data1),period2_data1[-1]]

            # When there is no valid data, we will add a row in the spreadsheet telling 
            # it is invalid, but we will not upload info to the server
            else:
                p2_row_data += ["Invalid","Invalid","Invalid","Invalid","Invalid"]

            if config.cte_verbose:
                print(sensabbrev," period2 tstamp: ",p2_row_data[0])
                print(sensabbrev," period2 min status1: ",p2_row_data[1])
                print(sensabbrev," period2 max status1: ",p2_row_data[2])
                print(sensabbrev," period2 min value1: ",p2_row_data[3])
                print(sensabbrev," period2 max value1: ",p2_row_data[4])
                print(sensabbrev," period2 mean value1: ",p2_row_data[5])            
                print(sensabbrev," period2 median value1: ",p2_row_data[6])            
                print(sensabbrev," period2 current value1: ",p2_row_data[7])

            ##### Second sensor handling
            # Let's add the min and max values of the status, to know if during the 
            # series we received errors
            p2_row_data += [min(period2_status2),max(period2_status2)]

            # If we obtained at least one valid data, we will make statistics and append the resulting
            # data to the record
            if (len(period2_data2) > 0):
                p2_row_data += [min(period2_data2),max(period2_data2),statistics.mean(period2_data2),statistics.median(period2_data2),period2_data2[-1]]

            # When there is no valid data, we will add a row in the spreadsheet telling 
            # it is invalid, but we will not upload info to the server
            else:
                p2_row_data += ["Invalid","Invalid","Invalid","Invalid","Invalid"]

            if config.cte_verbose:
                print(sensabbrev," period2 min status2: ",p2_row_data[8])
                print(sensabbrev," period2 max status2: ",p2_row_data[9])
                print(sensabbrev," period2 min value2: ",p2_row_data[10])
                print(sensabbrev," period2 max value2: ",p2_row_data[11])
                print(sensabbrev," period2 mean value2: ",p2_row_data[12])
                print(sensabbrev," period2 median value2: ",p2_row_data[13])
                print(sensabbrev," period2 current value2: ",p2_row_data[14])

            # Append the new record as a row in the spreadsheet
            p2_sheet_data += [p2_row_data]

            # print(p2_sheet_data)

            # In the case we have arrived to the maximum number of rows in the spreadsheet
            # we have to save it to disk, and empty the sheet data (preparing a new spreadsheet)
            if (i2_row >= period2_max_rows):
                # Store the current spreadsheet
                sheet_data2.update({"Data": p2_sheet_data})
                dt_string = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                if config.cte_verbose:
                    print("Closing period2 (current) file with tstamp " + dt_string)
                save_data(sensabbrev+"_p2_"+dt_string+".ods", sheet_data1)

                # Prepare the new spreadsheet
                sheet_data2 = OrderedDict()
                p2_sheet_data = [px_header]
                i2_row = 1
                if config.cte_verbose:
                    print("Opening period2 (new) file")

            else:
                # If the file can have more rows, we simply increase the counter of rows
                i2_row = i2_row + 1

            # As we have finished with the series, we restart the series counter
            # and empty the storage vectors
            i2 = 1
            period2_status1 = []
            period2_data1 = []
            period2_status2 = []
            period2_data2 = []

        else:
            # In the case it was not the last sample of the serie
            # We will increase the counter of samples
            i2 = i2 + 1
