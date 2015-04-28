import applications.Mutate.models.mutate_projects.findProjects as findProjects
from applications.Mutate.models.mutate_projects.mutatemutipleprojects import MutateMutipleProjects
from applications.Mutate.models.mutate_projects.mutateSingleProject import MutateSingleProject


def find_projects_task(keyword, maxsize, minsize, language, sortby,
                       orderby, number_of_projects, username, token, source_forge, mutation_tool):
    # find = findProjects.FindProjects()
    task_id = W2P_TASK.id
    # task = db((db.scheduler_task.status != 'FAILED') &
    #           (db.scheduler_task.vars == str(dict("keyword":keyword, maxsize=maxsize, minsize=minsize,
    #  language=language,
    #                                           sortby=sortby,orderby=orderby, number_of_projects=number_of_projects,
    #                                           username=username, token=token)))).select().last().id
    # find.search_github(keyword, maxsize, minsize, language, sortby,
    #                   orderby, number_of_projects, username, token, task_id)
    run = MutateMutipleProjects()
    search_terms = {}
    # Set others to False
    search_terms['team_name'] = False
    search_terms['repo_name'] = False
    # Search Terms
    search_terms['keyword'] = keyword
    search_terms['maxsize'] = maxsize
    search_terms['minsize'] = minsize
    search_terms['language'] = language
    search_terms['sortby'] = sortby
    search_terms['orderby'] = orderby
    search_terms['number_of_projects'] = number_of_projects

    authentication = {}
    authentication['username'] = username
    authentication['token'] = token
    run.main(search_terms, authentication, task_id, source_forge, mutation_tool)
    return dict(result="done")


def mutate_single_project_task(team_name, repo_name, source_forge, mutation_tool):
    task_id = W2P_TASK.id
    run = MutateSingleProject()

    search_terms = {}
    # Set others to False
    search_terms['team_name'] = team_name
    search_terms['repo_name'] = repo_name
    # Search Terms
    search_terms['keyword'] = False
    search_terms['maxsize'] = False
    search_terms['minsize'] = False
    search_terms['language'] = False
    search_terms['sortby'] = False
    search_terms['orderby'] = False
    search_terms['number_of_projects'] = False

    authentication = {}
    authentication['username'] = False
    authentication['token'] = False

    run.main(search_terms, authentication, task_id, source_forge, mutation_tool)

    return dict(result="done")

from gluon.scheduler import Scheduler

scheduler = Scheduler(db, tasks=dict(findProjects=find_projects_task, mutateSingleProject=mutate_single_project_task))
