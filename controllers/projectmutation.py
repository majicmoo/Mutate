__author__ = 'Megan'

import glob
import os
import ast

CLONED_REPOS_PATH = os.path.join("applications", "Mutate" ,"models" , "mutate_projects" ,"cloned_repos")


@auth.requires_login(otherwise=URL('default','login.html'))
def results():
    task_id=request.args(0)
    task=db(db.scheduler_task.id==int(task_id)).select().first()
    no_of_projects = task.vars.split(",")[5].split(":")[1]
    temp = None
    if task.status != "COMPLETED":
        current_number_of_projects_downloaded = 0
        for files in os.walk(CLONED_REPOS_PATH+os.sep+str(task_id)):
            current_number_of_projects_downloaded = len(map(int, files[1]))
            break

        current_number_of_projects_downloaded -= 1
        if current_number_of_projects_downloaded < 1:
            current_number_of_projects_downloaded =0

        else:
            try:
                temp_project = get_project(task_id, current_number_of_projects_downloaded)
                username = db.auth_user[auth._get_user_id()].username
                if db((db.project.clone_url==temp_project[1]) &(db.project.task_number==task_id)).select().first() is None:
                    db.project.insert(clone_url=temp_project[1], name=temp_project[0] ,
                                                  programming_language=temp_project[2],url=temp_project[3],
                                                  repo_size=temp_project[4],pom_location=temp_project[5],
                                                  current_username=username, task_number=task_id)
                    print temp_project[0] + ' added to database'
            except IOError:
                pass
    else:
        current_number_of_projects_downloaded = int(no_of_projects)
    results = H1('Found '+str(current_number_of_projects_downloaded)+' of ' + str(no_of_projects) + ' projects.')
    projects =  db(db.project.task_number == task_id).select()
    if task.status == "COMPLETED":
        results = H1('Search Results')
        print 'er' ,len(projects), current_number_of_projects_downloaded
        if len(projects) < current_number_of_projects_downloaded:
            temp_project = get_project(task_id, current_number_of_projects_downloaded)
            username = db.auth_user[auth._get_user_id()].username
            db.project.insert(clone_url=temp_project[1], name=temp_project[0] ,
                                                  programming_language=temp_project[2],url=temp_project[3],
                                                  repo_size=temp_project[4],pom_location=temp_project[5],
                                                  current_username=username, task_number=task_id)
    projects =  db(db.project.task_number == task_id).select()
    output=[]
    for i in projects:
        output.append(DIV(H2(A(i.name, _href = i.clone_url)), _class="well"))




    return dict(results=results, temp=temp, output=output, task_status = task.status)

def get_project(task_id, current_number_of_projects_downloaded):
    f = open(CLONED_REPOS_PATH+os.sep+str(task_id)+os.sep+'project_descriptors.txt', "r")
    f_list = f.readlines()
    f.close()
    start_line = (int(current_number_of_projects_downloaded)-1)*6
    return f_list[start_line:start_line+6]



def currentsearches():
    return dict(dict=dict)