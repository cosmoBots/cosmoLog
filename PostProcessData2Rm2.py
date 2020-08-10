#!/usr/bin/env python
# coding: utf-8

# In[ ]:

write_server = True
write_thingsboard = False #True

import config_tb
import requests
import time
from datetime import datetime

from redminelib import Redmine
import config_rm
import config_rm2

if config_rm.rm_ignore_cert:
    redmine = Redmine(config_rm.rm_server_url,key=config_rm.rm_key_txt, requests={'verify': False})
else:
    redmine = Redmine(config_rm.rm_server_url,key=config_rm.rm_key_txt)

projects = redmine.project.all()

print("Proyectos:")
for p in projects:
    print ("\t",p.identifier," \t| ",p.name)

my_project = redmine.project.get(config_rm.rm_project_id_str)
print ("Obtenemos proyecto: ",my_project.identifier," | ",my_project.name)

tmp = redmine.issue.filter(project_id=config_rm.rm_project_id_str, tracker_id=config_rm.rm_tracker_id, status_id=config_rm.rm_status_new_id)
project_data = sorted(tmp, key=lambda k: k.id)


# Borramos los datos de "Press1" ya que no se usan

# In[ ]:

if config_rm2.rm_ignore_cert:
    rm_dest = Redmine(config_rm2.rm_server_url,key=config_rm2.rm_key_txt, requests={'verify': False})
else:
    rm_dest = Redmine(config_rm2.rm_server_url,key=config_rm2.rm_key_txt)

rm_prj_dest = rm_dest.project.get(config_rm2.rm_project_id_str)
print ("Obtenemos proyecto destino: ",rm_prj_dest.identifier," | ",rm_prj_dest.name)

for datum in project_data:
    if (datum.category.id == config_rm.rm_cat_press1):
        print(datum)
        datum.delete()
        
    else:
        value = float(datum.custom_fields.get(config_rm.rm_cfield_value).value)
        # veo el valor
        minvalue = float(datum.custom_fields.get(config_rm.rm_cfield_min).value)
        maxvalue = float(datum.custom_fields.get(config_rm.rm_cfield_max).value)
        meanvalue = float(datum.custom_fields.get(config_rm.rm_cfield_mean).value)
        medianvalue = float(datum.custom_fields.get(config_rm.rm_cfield_median).value)

        # Cambiamos a 0 los valores que no estén bien
        if (datum.category.id == config_rm.rm_cat_temp1) or (datum.category.id == config_rm.rm_cat_temp2):
            print("Tratamos temperaturas")
            minstatus = int(datum.custom_fields.get(config_rm.rm_cfield_minstatus).value)
            print("minstatus",minstatus)
            if (minstatus == 96):
                print("value:",float(datum.custom_fields.get(config_rm.rm_cfield_value).value))
                value = 0.0
                # veo el valor 
                minvalue = 0.0
                maxvalue = 0.0
                meanvalue = 0.0
                medianvalue = 0.0
                print("Pongo a cero los valores erróneos")

        if (write_server):
            dest_iss = rm_dest.issue.create(project_id = rm_prj_dest.id,
               tracker_id = config_rm2.rm_tracker_id,
               subject = datum.subject,
               category_id = datum.category.id,
               custom_fields=[
                   {'id': config_rm2.rm_cfield_value,'value': value},
                   {'id': config_rm2.rm_cfield_minstatus,'value': datum.custom_fields.get(config_rm.rm_cfield_minstatus).value},
                   {'id': config_rm2.rm_cfield_maxstatus,'value': datum.custom_fields.get(config_rm.rm_cfield_maxstatus).value},
                   {'id': config_rm2.rm_cfield_min,'value':  minvalue},
                   {'id': config_rm2.rm_cfield_max,'value':  maxvalue},
                   {'id': config_rm2.rm_cfield_mean,'value':  meanvalue},
                   {'id': config_rm2.rm_cfield_median,'value':  medianvalue},
                   {'id': config_rm2.rm_cfield_samples,'value': datum.custom_fields.get(config_rm.rm_cfield_samples).value},
                   {'id': config_rm2.rm_cfield_tstamp,'value': datum.custom_fields.get(config_rm.rm_cfield_tstamp).value}
               ]
              )
            
            if (write_thingsboard):
                print(config_tb.telemetry_address)
                client_ts = datum.custom_fields.get(config_rm.rm_cfield_tstamp).value
                d = datetime.strptime(client_ts, "%Y-%m-%d %H:%M:%S")
                unixtime = int(time.mktime(d.timetuple())*1000)
                if (datum.category.id == config_rm.rm_cat_press1):
                    category = 'Pres1'
                if (datum.category.id == config_rm.rm_cat_press2):
                    category = 'Pres2'
                if (datum.category.id == config_rm.rm_cat_temp1):
                    category = 'Temp1'
                if (datum.category.id == config_rm.rm_cat_temp2):
                    category = 'Temp2'
                
                pload = {'ts':unixtime, "values":{category+'_value':999.99,category+'_category':category,category+'_minstatus':1515,category+'_maxstatus':1510,
                         category+'_min':1000.0,category+'_max':998.00, category+'_mean':1515.0, category+'_median':1516.0,category+'_samples':0,category+'_tstamp':client_ts}}
                print(pload)
                print("========")
                r = requests.post(config_tb.telemetry_address,json = pload)
                print(r)
                
            if (dest_iss is not None):
                print(datum.id,"-->",dest_iss.id)
                datum.delete()



