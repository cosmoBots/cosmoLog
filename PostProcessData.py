#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from redminelib import Redmine
from config_rm import *

redmine = Redmine(rm_server_url,key=rm_key_txt)
projects = redmine.project.all()

print("Proyectos:")
for p in projects:
    print ("\t",p.identifier," \t| ",p.name)

my_project = redmine.project.get(rm_project_id_str)
print ("Obtenemos proyecto: ",my_project.identifier," | ",my_project.name)

tmp = redmine.issue.filter(project_id=rm_project_id_str, tracker_id=rm_tracker_id, status_id=rm_status_new_id)
project_data = sorted(tmp, key=lambda k: k.id)


# Borramos los datos de "Press1" ya que no se usan

# In[ ]:


for datum in project_data:
    tstamp = datum.custom_fields.get(rm_cfield_tstamp).value
    if ':' not in tstamp:
        newtstamp = tstamp[:10] +' '+ tstamp[11:13] + ':' + tstamp[13:15] + ':' + tstamp[15:17]
    else:
        newtstamp = tstamp
        print("New tstamp")

    
    if (datum.category.id == rm_cat_press2):
            print("Status:",datum.status.name)
            value = float(datum.custom_fields.get(rm_cfield_value).value) * 1e9
            # veo el valor 
            minvalue = float(datum.custom_fields.get(rm_cfield_min).value) * 1e9
            maxvalue = float(datum.custom_fields.get(rm_cfield_max).value) * 1e9
            meanvalue = float(datum.custom_fields.get(rm_cfield_mean).value) * 1e9
            medianvalue = float(datum.custom_fields.get(rm_cfield_median).value) * 1e9
            print("actualizamos a value:",value)
            print("actualizamos a minvalue:",minvalue)
            print("actualizamos a maxvalue:",maxvalue)
            print("actualizamos a meanvalue:",meanvalue)
            print("actualizamos a medianvalue:",medianvalue)
            redmine.issue.update(resource_id=datum.id,
                 status_id = rm_status_converted_id,
                 custom_fields=[{'id': rm_cfield_value,'value': value},
                                {'id': rm_cfield_min,'value': minvalue},
                                {'id': rm_cfield_max,'value': maxvalue},
                                {'id': rm_cfield_mean,'value': meanvalue},
                                {'id': rm_cfield_median,'value': medianvalue},
                                {'id': rm_cfield_tstamp,'value': newtstamp}
                                ]
            )
    else:
        # Cambiamos a 0 los valores que no estén bien
        if (datum.category.id == rm_cat_temp1) or (datum.category.id == rm_cat_temp2):
            print("Tratamos temperaturas")
            minstatus = int(datum.custom_fields.get(rm_cfield_minstatus).value)
            print("minstatus",minstatus)
            if (minstatus == 96):
                print("tstamp:",newtstamp)
                print("value:",float(datum.custom_fields.get(rm_cfield_value).value))
                value = 0.0
                # veo el valor 
                minvalue = 0.0
                maxvalue = 0.0
                meanvalue = 0.0
                medianvalue = 0.0
                redmine.issue.update(resource_id=datum.id,
                     status_id = rm_status_converted_id,
                     custom_fields=[{'id': rm_cfield_value,'value': value},
                                    {'id': rm_cfield_min,'value': minvalue},
                                    {'id': rm_cfield_max,'value': maxvalue},
                                    {'id': rm_cfield_mean,'value': meanvalue},
                                    {'id': rm_cfield_median,'value': medianvalue},
                                    {'id': rm_cfield_tstamp,'value': newtstamp}
                                    ]
                )
            else:
                redmine.issue.update(resource_id=datum.id,
                     status_id = rm_status_converted_id,
                     custom_fields=[{'id': rm_cfield_tstamp,'value': newtstamp}]
                )





