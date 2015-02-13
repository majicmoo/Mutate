import os
from applications.Mutate.models.mutate_projects.project import Project
from applications.Mutate.models.mutate_projects.github import Github
from applications.Mutate.models.mutate_projects.pit import Pit


# Variables for Java and Pit
NUMBER_OF_MAVEN_FILES = 1  # Number of pom.xml each project must have
#CLONED_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_repos")
CLONED_REPOS_PATH = 'cloned_repos'
MAX_JUNIT_TESTS = 40  # maximum number of junit tests
MIN_JUNIT_TESTS = 0  # minimum number of junit tests


class Main(object):

    def __init__(self):
        self.languages = ["python", "java", "ruby", "c"]  # languages accepted
        self.project_storage = []  # Accepted projects array

    def main(self, keyword, maxsize, minsize, language, sort_by, order_by, number_of_projects, username, token, task,
             source_forge, mutation_tool):

        # Check to see if language is supported
        if language not in self.languages:
            print "DEBUG:", language, "is not supported."
            return False

        # Create directory for current user search
        current_directory = os.path.join(CLONED_REPOS_PATH, str(task))
        print "DEBUG:", "Creating task directory:",current_directory
        os.makedirs(current_directory)

        # Initialise sourceforge
        if source_forge == "Github":
            search = Github(keyword, maxsize, minsize, language, sort_by, order_by, username, token, task, current_directory)
            search_result = search.initial_search()
        else:
            # Another sourceforge could be set up here
            # e.g.
            # search = Bitbucket(args)
            # search_result = search.initial_search_bitbucket()
            # bitbucket must extend SourceForge
            print "DEBUG:", source_forge, "is not supported"
            return False

        # Initialise tool
        if mutation_tool == "pit":
            tool = Pit(None)
        else:
            # Another tool could be set up here
            # e.g.
            # tool = SomeTool(args)
            # SomeTool must extend MutationTool
            print "DEBUG:", mutation_tool, "is not supported"
            return False



        # Loop until the required amount of projects are found.
        while len(self.project_storage) < number_of_projects:
            requirements_met = tool.check_requirements(search, search_result)
            # If project has required fields get project from sourceforge
            if requirements_met:
                # Put project in project format
                current_project = Project(search.get_current_project())
                tool.set_current_project(current_project)
                # Get project from sourceforge
                cloned_project_path = search.clone_repo(current_project)
                # Run setup for tool
                setup_passed = tool.run_setup(cloned_project_path)
                if setup_passed:
                    self.project_storage.append(current_project)
                    print "Appending", current_project.name, "to project_descriptors.txt"
                    with open(os.path.join(current_directory, 'project_descriptors.txt'), "a") as my_file:
                        my_file.write(str(current_project.name) + '\n' +
                                      str(current_project.clone[:-4]) + '\n' +
                                      str(current_project.language) + '\n' +
                                      str(current_project.url) + '\n' +
                                      str(current_project.size) + '\n' +
                                      str(current_project.pom_location) + '\n')
            #         # # Run tool
            #         # tool_ran_successfully = tool.run(cloned_project_path)
            #         # # if tool ran successfully add project to storage and write to file
            #         # if tool_ran_successfully:
            #         #     self.project_storage.append(current_project)
            #         #     print "Appending", current_project.name, "to project_descriptors.txt"
            #         #     with open(os.path.join(current_directory, 'project_descriptors.txt'), "a") as my_file:
            #         #         my_file.write(str(current_project.name) + '\n' +
            #         #                       str(current_project.clone[:-4]) + '\n' +
            #         #                       str(current_project.language) + '\n' +
            #         #                       str(current_project.url) + '\n' +
            #         #                       str(current_project.size) + '\n' +
            #         #                       str(current_project.pom_location) + '\n')
            # Get next search result
            search_result = search.get_next_search_result()

