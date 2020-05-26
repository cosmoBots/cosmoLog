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
    if (datum.category.name == "Pres1"):
        print(datum)
        datum.delete()


# 
# 

# In[ ]:





# In[ ]:





# In[ ]:




