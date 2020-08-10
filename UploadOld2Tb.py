#!/usr/bin/env python
# coding: utf-8

# In[ ]:

write_server = True
write_thingsboard = True

import config_tb
import requests
import time
from datetime import datetime

from redminelib import Redmine
import config_rm2

if config_rm2.rm_ignore_cert:
    redmine = Redmine(config_rm2.rm_server_url,key=config_rm2.rm_key_txt, requests={'verify': False})
else:
    redmine = Redmine(config_rm2.rm_server_url,key=config_rm2.rm_key_txt)

projects = redmine.project.all()

print("Proyectos:")
for p in projects:
    print ("\t",p.identifier," \t| ",p.name)

my_project = redmine.project.get(config_rm2.rm_project_id_str)
print ("Obtenemos proyecto: ",my_project.identifier," | ",my_project.name)

tmp = redmine.issue.filter(project_id=config_rm2.rm_project_id_str, 
                           tracker_id=config_rm2.rm_tracker_id, 
                           status_id=config_rm2.rm_status_new_id,limit=50)
print("hornada:",len(tmp))
done = len(tmp)<=0 

while not(done):
    project_data = sorted(tmp, key=lambda k: k.id)

    # Borramos los datos de "Press1" ya que no se usan

    # In[ ]:

    for datum in project_data:
            value = float(datum.custom_fields.get(config_rm2.rm_cfield_value).value)
            # veo el valor
            minvalue = float(datum.custom_fields.get(config_rm2.rm_cfield_min).value)
            maxvalue = float(datum.custom_fields.get(config_rm2.rm_cfield_max).value)
            meanvalue = float(datum.custom_fields.get(config_rm2.rm_cfield_mean).value)
            medianvalue = float(datum.custom_fields.get(config_rm2.rm_cfield_median).value)

            if (write_thingsboard):
                print(config_tb.telemetry_address)
                client_ts = datum.custom_fields.get(config_rm2.rm_cfield_tstamp).value
                d = datetime.strptime(client_ts, "%Y-%m-%d %H:%M:%S")
                unixtime = int(time.mktime(d.timetuple())*1000)
                print("CATEGORY: ",datum.category.id)
                if (datum.category.id == config_rm2.rm_cat_press1):
                    category = 'Pres1'
                if (datum.category.id == config_rm2.rm_cat_press2):
                    category = 'Pres2'
                if (datum.category.id == config_rm2.rm_cat_temp1):
                    category = 'Temp1'
                if (datum.category.id == config_rm2.rm_cat_temp2):
                    category = 'Temp2'

                pload = {'ts':unixtime, "values":{category+'_value':value,
                                                  category+'_category':category,
                                                  category+'_minstatus':datum.custom_fields.get(config_rm2.rm_cfield_minstatus).value,
                                                  category+'_maxstatus':datum.custom_fields.get(config_rm2.rm_cfield_maxstatus).value,   
                                                  category+'_min':minvalue,
                                                  category+'_max':maxvalue, category+'_mean':meanvalue,
                                                  category+'_median':medianvalue,
                                                  category+'_samples':datum.custom_fields.get(config_rm2.rm_cfield_samples).value,
                                                  category+'_tstamp':client_ts}}
                print(pload)
                print("========")
                r = requests.post(config_tb.telemetry_address,json = pload)
                print(r.status_code)
                if (r.status_code == 200):
                    redmine.issue.update(datum.id,status_id=config_rm2.rm_status_converted_id)
            
    tmp = redmine.issue.filter(project_id=config_rm2.rm_project_id_str, 
                               tracker_id=config_rm2.rm_tracker_id, 
                               status_id=config_rm2.rm_status_new_id,limit=200)
    print("hornada:",len(tmp))
    done = len(tmp)<=0 
    
print("Acabamos!!!")


