__author__ = 'Megan'
from applications.Mutate.models.testinggithubapi.findProjects import FindProjects

class Main(object):

    def __init__(self, keyword, maxsize, minsize, language, sortby,
                      orderby, number_of_projects, username, token, task_id):
        # Search for project
        FindProjects().search_for_projects(keyword, maxsize, minsize, language, sortby,
                      orderby, number_of_projects, username, token, task_id)
        # Clone project
        # run mvn
        # run mutation tool
        pass
