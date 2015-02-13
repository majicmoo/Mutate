class SourceForge(object):

    def __init__(self, keyword, maxsize, minsize, language, sort_by, order_by, username, token, task, cloned_repo_path):
        self.keyword = keyword
        self.maxsize = maxsize
        self.minsize = minsize
        self.language = language
        self.sort_by = sort_by
        self.order_by = order_by
        self.username = username
        self.token = token
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