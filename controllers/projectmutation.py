__author__ = 'Megan'

import glob
import os
import ast

CLONED_REPOS_PATH = "applications/Mutate/models/testinggithubapi/clonedrepos"


@auth.requires_login(otherwise=URL('default','login.html'))
def results():
    task_id=request.args(0)
    task=db(db.scheduler_task.id==int(task_id)).select().first()
    no_of_projects = task.vars.split(",")[5].split(":")[1]
    temp = None
    if task.status != "COMPLETED":
        current_number_of_projects_downloaded = 0
        for files in os.walk(CLONED_REPOS_PATH+"/"+str(task_id)):
            current_number_of_projects_downloaded = len(map(int, files[1]))
            print current_number_of_projects_downloaded
            break

        current_number_of_projects_downloaded -= 1
        if current_number_of_projects_downloaded < 1:
            current_number_of_projects_downloaded =0

        else:
            try:
                f = open(CLONED_REPOS_PATH+"/"+str(task_id)+'/'+'projectdescriptors.txt', "r")
                f_list = f.readlines()
                f.close()
                start_line = (current_number_of_projects_downloaded-1)*6
                temp_project = f_list[start_line:start_line+6]
                username = db.auth_user[auth._get_user_id()].username
                if db(db.project.clone_url==temp_project[1]).select().first() is None:
                    db.project.insert(clone_url=temp_project[1], name=temp_project[0] ,
                                                  programming_language=temp_project[2],url=temp_project[3],
                                                  repo_size=temp_project[4],pom_location=temp_project[5],
                                                  current_username=username)
            except IOError:
                pass
    else:
        current_number_of_projects_downloaded = no_of_projects




    results = H1('Found '+str(current_number_of_projects_downloaded)+' of ' + str(no_of_projects) + ' projects.')
    return dict(results=results, temp=temp)

def currentsearches():
    return dict(dict=dict)