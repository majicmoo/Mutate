import os
from applications.Mutate.models.mutate_projects.project import Project
from applications.Mutate.models.mutate_projects.githubFunctions import GithubFunctions
from applications.Mutate.models.mutate_projects.cloneProject import CloneProject
from applications.Mutate.models.mutate_projects.runMaven import RunMaven
from applications.Mutate.models.mutate_projects.pit import Pit


# Variables for Java and Pit
NUMBER_OF_MAVEN_FILES = 1  # Number of pom.xml each project must have
CLONED_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_repos")
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

        # Initialise search depending on repository
        if source_forge == "Github":
            search = GithubFunctions(keyword, maxsize, minsize, language, sort_by, order_by, username, token, task)
            search_result = search.initial_search()
        else:
            # Another sourceforge could be set up here
            # e.g.
            # search = BitbucketFunctions(args)
            # search_result = search.initial_search_bitbucket()
            print "DEBUG:", source_forge, "is not supported"
            return False

        # Create directory for current user search
        os.makedirs(CLONED_REPOS_PATH + os.sep + str(task))
        cloned_path = CLONED_REPOS_PATH + os.sep + str(task)

        # Loop until the required amount of projects are found.
        while len(self.project_storage) < number_of_projects:
            # Reset variables
            tool_ran_successfully = False
            get_project = False

            # Check current project has required files
            if language == "java":
                # check for junit tests and maven files
                search_for_mvn = search.search_for_mvn(search_result)["total_count"]
                if search_for_mvn == NUMBER_OF_MAVEN_FILES:
                    search_for_junit = search.search_repo_for_junit_tests(search_result)["total_count"]
                    # if search_for_junit < MAX_JUNIT_TESTS and search_for_junit > MIN_JUNIT_TESTS:
                    if MIN_JUNIT_TESTS < search_for_junit < MAX_JUNIT_TESTS:
                        get_project = True

            # If project has required fields get project from sourceforge
            if get_project:
                # Put project in project format
                current_project = Project(search.get_current_project())
                # Get project from sourceforge
                cloned_project_path = search.clone_repo(current_project)
                # Run Mutation Tool
                if language == "java":
                    # run maven
                    run_maven = RunMaven(current_project).run_maven(cloned_project_path)
                    if run_maven:
                        if mutation_tool == "pit":
                            # run pit
                            tool_ran_successfully = Pit().run(RunMaven(current_project).find_pom(cloned_project_path))
                else:
                    print "DEBUG:", language, "is not supported"

                # if tool ran successfully add project to storage and write to file
                if tool_ran_successfully:
                    self.project_storage.append(current_project)
                    print "Appending", current_project.name, "to project_descriptors.txt"
                    with open(CLONED_REPOS_PATH + os.sep + str(task) + os.sep + 'project_descriptors.txt', "a")\
                            as my_file:
                        my_file.write(str(current_project.name) + '\n' +
                                      str(current_project.clone[:-4]) + '\n' +
                                      str(current_project.language) + '\n' +
                                      str(current_project.url) + '\n' +
                                      str(current_project.size) + '\n' +
                                      str(current_project.pom_location) + '\n')
            # Get next search result
            search_result = search.get_next_search_result()