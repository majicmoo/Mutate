import time

SLEEP_TIME = 60  # Time between API accesses when reached rate limit


class SourceForge(object):

    def __init__(self, search_terms, authentication, task, cloned_repo_path):
        self.keyword = search_terms['keyword']
        self.maxsize = search_terms['maxsize']
        self.minsize = search_terms['minsize']
        self.language = search_terms['language']
        self.sort_by = search_terms['sortby']
        self.order_by = search_terms['orderby']
        self.number_of_projects = search_terms['number_of_projects']

        self.team_name = search_terms['team_name']
        self.repo_name = search_terms['repo_name']

        self.username = authentication['username']
        self.token = authentication['token']

        self.task = task
        self.clone_repo_path = cloned_repo_path

    def initial_search(self):
        pass

    def get_next_search_result(self):
        pass

    def get_current_project(self):
        pass

    def clone_repo(self, project):
        pass

    def get_single_project(self):
        pass

    def sleep_search(self):
        print "DEBUG sleep:", SLEEP_TIME, "seconds"
        time.sleep(SLEEP_TIME)