__author__ = 'Megan'

import os

CLONED_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_repos")
CLONED_SINGLE_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_single_repos")
INDEX_PATH = os.path.join("applications", "Mutate", "static", "index")
NO_OF_LINES_IN_PROJECT_DESCRIPTOR = 6


@auth.requires_login(otherwise=URL('default', 'login.html'))
def results():
    # get current task id
    task_id = request.args(0)
    # get current task
    task = db(db.scheduler_task.id == int(task_id)).select().first()

    if task is None:
        redirect(URL('default', 'index.html'))

    # get number of projects required
    no_of_projects = task.vars.split(",")[7].split(":")[1]
    # get current list of projects
    projects = db(db.project.task_number == task_id).select()
    username = db.auth_user[auth._get_user_id()].username

    try:
        current_path = os.path.join(CLONED_REPOS_PATH, str(task_id))
        f = open(os.path.join(current_path, 'project_descriptors.txt'), "r")
        f_list = f.readlines()
        f.close()
        current_number_of_projects_downloaded = len(f_list)
        if current_number_of_projects_downloaded > len(projects):
            for i in range(current_number_of_projects_downloaded):
                temp_project = f_list[i].split(',')
                if len(temp_project) != 0:
                    if db.project((db.project.name == temp_project[0]) & (db.project.task_number == task_id)) is None:
                        db.project.insert(clone_url=temp_project[1], name=temp_project[0],
                                          programming_language=temp_project[2], url=temp_project[3],
                                          repo_size=temp_project[4], pom_location=temp_project[5],
                                          current_username=username, task_number=task_id,
                                          mutation_score=temp_project[6])
                        print 'DEBUG: ', temp_project[0] + ' added to database'
                        # Reload updated projects
                        projects = db(db.project.task_number == task_id).select()
    except IOError:
        current_number_of_projects_downloaded = 0

    no_of_results = H1('Found '+str(current_number_of_projects_downloaded)+' of ' + str(no_of_projects) + ' projects.')
    output = []
    list_of_projects = []
    for i in projects:
        results = os.path.join('applications', 'Mutate', 'static', 'index', str(task_id), str(i.name), 'index.html')
        if os.path.isfile(results):
            output.append(DIV(DIV(H2(A(i.name, _href=i.clone_url,)), _class='span8'),
                              DIV(H2(i.mutation_score + '%'), _class='span2 pull-right'),
                              DIV(P(A('More...', _href=URL('static', 'index/' + str(task_id) + '/' + str(i.name) +
                                                           '/index.html'))), _class='span12'), _class="well span12"))
        else:
            output.append(DIV(DIV(H2(A(i.name, _href=i.clone_url,)), _class='span8'),
                              DIV(H2(i.mutation_score + '%'), _class='span2 pull-right'),
                              _class="well span12"))
        list_of_projects.append(i.name)

    return dict(results=no_of_results, output=output, task_status = task.status, task_id=task_id,
                list_of_projects=list_of_projects)


def result():
    task_id = request.args(0)
    # get current task
    output = []
    task = db(db.scheduler_task.id == int(task_id)).select().first()
    if auth._get_user_id() is not None:
        username = db.auth_user[auth._get_user_id()].username
    else:
        username = None

    if task is None:
        redirect(URL('default', 'index.html'))

    i = None

    try:
        current_path = os.path.join(CLONED_SINGLE_REPOS_PATH, str(task_id))
        f = open(os.path.join(current_path, 'project_descriptors.txt'), "r")
        temp_project = f.readlines()[0].split(',')
        f.close()
        db.project.insert(clone_url=temp_project[1], name=temp_project[0], programming_language=temp_project[2],
                          url=temp_project[3], repo_size=temp_project[4], pom_location=temp_project[5],
                          current_username=username, task_number=task_id, mutation_score=temp_project[6])
        i = db(db.project.task_number == task_id).select().first()
        results = os.path.join('applications', 'Mutate', 'static', 'index', str(task_id), str(i.name), 'index.html')
        if os.path.isfile(results):
            output.append(DIV(DIV(H2(A(i.name, _href=i.clone_url,)), _class='span8'),
                              DIV(H2(i.mutation_score + '%'), _class='span2 pull-right'),
                              DIV(P(A('More...', _href=URL('static', 'index/' + str(task_id) + '/' + str(i.name) +
                                                           '/index.html'))), _class='span12'), _class="well span12"))
        else:
            output.append(DIV(DIV(H2(A(i.name, _href=i.clone_url,)), _class='span8'),
                              DIV(H2(i.mutation_score + '%'), _class='span2 pull-right'),
                              _class="well span12"))

    except IOError:
        output.append("Project is being mutated")


    return dict(output=output, task_id=task_id, i=i, task_status = task.status)


def currentsearches():
    return dict(dict=dict)