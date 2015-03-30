class MutationTool(object):

    def __init__(self, project):
        self.project = project

    def check_requirements(self, search, search_result):
        # Check requirements for project are met
        pass

    def run_setup(self, project_location):
        # Run anything required to setup tool
        pass

    def run(self, current_file):
        # Run Mutation Tool
        pass

    def set_current_project(self, current_project):
        self.project = current_project

    def push_results(self, destination):
        pass