__author__ = 'Megan'

import glob
import os
import ast

CLONED_REPOS_PATH = os.path.join("applications", "Mutate" ,"models" , "mutate_projects" ,"cloned_repos")


@auth.requires_login(otherwise=URL('default','login.html'))
def results():
    # get current task id
    task_id=request.args(0)
    # get current task
    task=db(db.scheduler_task.id==int(task_id)).select().first()
    # get number of projects required
    no_of_projects = task.vars.split(",")[7].split(":")[1]
    # get current list of projects
    projects =  db(db.project.task_number == task_id).select()

    if task.status != "COMPLETED":
        if projects is not None:
            current_number_of_projects_downloaded = len(projects)
        else:
            current_number_of_projects_downloaded = 0
        try:
            # try to read project descriptors file, if there write projects to file
            if current_number_of_projects_downloaded == 0:
                temp = 1
            else:
                temp = current_number_of_projects_downloaded
            temp_project = get_project(task_id, temp)
            if len(temp_project) > 0:
                username = db.auth_user[auth._get_user_id()].username
                if db((db.project.clone_url==temp_project[1]) &(db.project.task_number==task_id)).select().first() is None:
                    db.project.insert(clone_url=temp_project[1], name=temp_project[0] ,
                                                  programming_language=temp_project[2],url=temp_project[3],
                                                  repo_size=temp_project[4],pom_location=temp_project[5],
                                                  current_username=username, task_number=task_id)
                    print temp_project[0] + ' added to database'
        except IOError:
                pass
        results = H1('Found '+str(current_number_of_projects_downloaded)+' of ' + str(no_of_projects) + ' projects.')
    else:
        if len(projects) < no_of_projects:
            temp_project = get_project(task_id, no_of_projects)
            username = db.auth_user[auth._get_user_id()].username
            db.project.insert(clone_url=temp_project[1], name=temp_project[0] ,
                              programming_language=temp_project[2],url=temp_project[3],
                              repo_size=temp_project[4],pom_location=temp_project[5],
                              current_username=username, task_number=task_id)

        current_number_of_projects_downloaded = no_of_projects
        results = H1('Search Results')

    output=[]
    for i in projects:
        output.append(DIV(H2(A(i.name, _href = i.clone_url)), _class="well"))




    return dict(results=results, output=output, task_status = task.status)

def get_project(task_id, current_number_of_projects_downloaded):
    f = open(os.path.join(CLONED_REPOS_PATH,str(task_id),'project_descriptors.txt'), "r")
    f_list = f.readlines()
    f.close()
    start_line = (int(current_number_of_projects_downloaded)-1)*6
    return f_list[start_line:start_line+6]



def currentsearches():
    return dict(dict=dict)