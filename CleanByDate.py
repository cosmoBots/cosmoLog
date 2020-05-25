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

tmp = redmine.issue.filter(project_id=rm_project_id_str, tracker_id=rm_tracker_id, status_id='*')
project_data = sorted(tmp, key=lambda k: k.id)


# Borramos todos los datos de una fecha concreta

# In[ ]:


for datum in project_data:
    tstamp = datum.custom_fields.get(rm_cfield_tstamp).value
    if (tstamp[:10]=="2020-05-23"):
        print(tstamp)
        datum.delete()


# In[ ]:





# In[ ]:





# In[ ]:




