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

project_data = redmine.issue.filter(project_id=rm_project_id_str, tracker_id=rm_tracker_id, status_id=rm_status_converted_id)
#project_data = sorted(tmp, key=lambda k: k.id)

my_cp_project = redmine.project.get("cryostat2")
max_id = 60000

# Borramos los datos de "Press1" ya que no se usan

for datum in project_data:
    if (datum.id <= max_id):
        print("Muevo:",datum.id)
        redmine.issue.update(resource_id=datum.id, project_id=my_cp_project.id)

