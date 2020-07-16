import config_rm
import config_rm2

print("Trasvase de incidencias entre dos proyectos en dos redmines")
prj_origen = "pfeiffer-test"
prj_destino = "pfeiffer-test"

print("Origen:",config_rm.rm_server_url,prj_origen)
print("Destino:",config_rm2.rm_server_url,prj_destino)

#Obtenemos las incidencias a traspasar
initial_issue = 112704

from redminelib import Redmine
rm_orig = Redmine(config_rm.rm_server_url,key=config_rm.rm_key_txt)
rm_prj_orig = rm_orig.project.get(config_rm.rm_project_id_str)
orig_issues = sorted(rm_prj_orig.issues, key=lambda k: k.id)
for iss in orig_issues:
    if (iss.id>=initial_issue):
        print(iss.id)


rm_dest = Redmine(config_rm2.rm_server_url,key=config_rm2.rm_key_txt)
print(rm_dest)

print("Proyectos:")
dest_projects = rm_dest.project.all()
for p in dest_projects:
    print ("\t",p.identifier," \t| ",p.name)

rm_prj_dest = rm_dest.project.get(config_rm2.rm_project_id_str)
write_server = True
for iss in orig_issues:
    if (iss.id>=initial_issue) and (iss.status.id == config_rm.rm_status_converted_id):
        print(iss.id)
        if (write_server):
            dest_iss = rm_dest.issue.create(project_id = rm_prj_dest.id,
               tracker_id = config_rm2.rm_tracker_id,
               subject = iss.subject,
               category_id = iss.category.id,
               custom_fields=[
                   {'id': config_rm2.rm_cfield_value,'value': iss.custom_fields.get(config_rm.rm_cfield_value).value},
                   {'id': config_rm2.rm_cfield_minstatus,'value': iss.custom_fields.get(config_rm.rm_cfield_minstatus).value},
                   {'id': config_rm2.rm_cfield_maxstatus,'value': iss.custom_fields.get(config_rm.rm_cfield_maxstatus).value},
                   {'id': config_rm2.rm_cfield_min,'value':  iss.custom_fields.get(config_rm.rm_cfield_min).value},
                   {'id': config_rm2.rm_cfield_max,'value':  iss.custom_fields.get(config_rm.rm_cfield_max).value},
                   {'id': config_rm2.rm_cfield_mean,'value':  iss.custom_fields.get(config_rm.rm_cfield_mean).value},
                   {'id': config_rm2.rm_cfield_median,'value':  iss.custom_fields.get(config_rm.rm_cfield_median).value},
                   {'id': config_rm2.rm_cfield_samples,'value': iss.custom_fields.get(config_rm.rm_cfield_samples).value},
                   {'id': config_rm2.rm_cfield_tstamp,'value': iss.custom_fields.get(config_rm.rm_cfield_tstamp).value}
               ]
              )
            if (dest_iss is not None):
                print(iss.id,"-->",dest_iss.id)
                iss.delete()

