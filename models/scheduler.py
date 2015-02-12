import applications.Mutate.models.mutate_projects.findProjects as findProjects
from applications.Mutate.models.mutate_projects.main import Main


def find_projects_task(keyword, maxsize, minsize, language, sortby,
                      orderby, number_of_projects, username, token, source_forge, mutation_tool):
    print "Hello"
    #find = findProjects.FindProjects()
    task_id = W2P_TASK.id
    # task = db((db.scheduler_task.status != 'FAILED') &
    #           (db.scheduler_task.vars == str(dict("keyword":keyword, maxsize=maxsize, minsize=minsize, language=language,
    #                                           sortby=sortby,orderby=orderby, number_of_projects=number_of_projects,
    #                                           username=username, token=token)))).select().last().id
    # find.search_github(keyword, maxsize, minsize, language, sortby,
    #                   orderby, number_of_projects, username, token, task_id)
    run = Main()
    run.main(keyword, maxsize, minsize, language, sortby,
                      orderby, number_of_projects, username, token, task_id, source_forge, mutation_tool)


    return dict(result="done")

from gluon.scheduler import Scheduler

scheduler = Scheduler(db, tasks=dict(findProjects=find_projects_task))
