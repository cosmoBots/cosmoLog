import sys
import config
import serial
from datetime import datetime
from collections import OrderedDict
from pyexcel_ods import save_data
import statistics
from config_rm import *
from redminelib import Redmine

redmine = Redmine(rm_server_url,key=rm_key_txt)
projects = redmine.project.all()

print("Proyectos:")
for p in projects:
    print ("\t",p.identifier," \t| ",p.name)

my_project = redmine.project.get(rm_project_id_str)
print ("Obtenemos proyecto: ",my_project.identifier," | ",my_project.name)    
    
sys.path.insert(0, './fsm')
import PfLog



def odsgen(catsens,sensabbrev,period1,period1_max_rows,px_header):

    filecounter = 0
    write_files = False
    write_server = True

    # Configuration
    valid_status_limit = 255  # maximum status code to store values in rows.  
                # If the status is greater than this maximum, the sample will not be added to the series
                # if the full set is invalid, it will not be uploaded to server, and it will be stored
                # as "invalid" in the files

    # Initialization for the row counters and spreadsheet preparation
    i1_row = 1
    sheet_data1 = OrderedDict() # from collections import OrderedDict

    p1_sheet_data = [px_header]
    voidFile = True
    p1_row_data = []

    tmp = redmine.issue.filter(project_id=rm_project_id_str, tracker_id=rm_tracker_id, status_id=rm_status_converted_id, category_id=catsens)
    rm_catsens = sorted(tmp, key=lambda k: k.id)    
    thisperiod = period1
    
    # Begin the endless loop which acquires from the device, processes, uploads and stores
    for datum in rm_catsens:
        thisperiod -= 1
        if (thisperiod == 0):
            thisperiod = period1
            voidFile = False
            p1_row_data = [datum.custom_fields.get(rm_cfield_tstamp).value]

            ##### First sensor handling
            # Let's add the min and max values of the status, to know if during the 
            # series we received errors
            p1_row_data += [datum.custom_fields.get(rm_cfield_minstatus).value,datum.custom_fields.get(rm_cfield_maxstatus).value]

            # If we obtained at least one valid data, we will make statistics and append the resulting
            # data to the record   
            p1_row_data += [datum.custom_fields.get(rm_cfield_min).value,datum.custom_fields.get(rm_cfield_max).value,
                            datum.custom_fields.get(rm_cfield_mean).value,datum.custom_fields.get(rm_cfield_median).value,
                            datum.custom_fields.get(rm_cfield_value).value]

            if config.cte_verbose:
                print(sensabbrev," period1 tstamp: ",p1_row_data[0])
                print(sensabbrev," period1 min status1: ",p1_row_data[1])
                print(sensabbrev," period1 max status1: ",p1_row_data[2])
                print(sensabbrev," period1 min value1: ",p1_row_data[3])
                print(sensabbrev," period1 max value1: ",p1_row_data[4])
                print(sensabbrev," period1 mean value1: ",p1_row_data[5])            
                print(sensabbrev," period1 median value1: ",p1_row_data[6])            
                print(sensabbrev," period1 current value1: ",p1_row_data[7])

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
                
                save_data(sensabbrev+"_"+str(filecounter)+"_"+dt_string+".ods", sheet_data1)
                filecounter += 1
                # Prepare the new spreadsheet
                sheet_data1 = OrderedDict()
                p1_sheet_data = [px_header]
                voidFile = True
                i1_row = 1
                if config.cte_verbose:
                    print("Opening period1 (new) file")

            else:
                # If the file can have more rows, we simply increase the counter of rows
                i1_row = i1_row + 1

    if not(voidFile):
        # Store the current spreadsheet
        sheet_data1.update({"Data": p1_sheet_data})
        dt_string = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        if config.cte_verbose:
            print("Closing period1 (current) file with tstamp " + dt_string)
        save_data(sensabbrev+"_"+str(filecounter)+"_"+dt_string+".ods", sheet_data1)
        

px_header = ["tstamp", "min status", "max status", "min press2 x 1e9", "max press2 x 1e9", "mean press2 x 1e9", "median press2 x 1e9","current press2 x 1e9"]        
odsgen(rm_cat_press2,"pres2p1",1,2880,px_header)
odsgen(rm_cat_press2,"pres2p2",20,144,px_header)
px_header = ["tstamp", "min status", "max status", "min temp2", "max temp2", "mean temp2", "median temp2","current temp2"]    
odsgen(rm_cat_temp2,"temp2p1",1,2880,px_header)
odsgen(rm_cat_temp2,"temp2p2",20,144,px_header)
px_header = ["tstamp", "min status", "max status", "min temp1", "max temp1", "mean temp1", "median temp1","current temp1"]    
odsgen(rm_cat_temp1,"temp1p1",1,2880,px_header)
odsgen(rm_cat_temp1,"temp1p2",20,144,px_header)
