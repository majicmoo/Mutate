import os
from applications.Mutate.models.mutate_projects.project import Project
from applications.Mutate.models.mutate_projects.github import Github
from applications.Mutate.models.mutate_projects.pit import Pit
from applications.Mutate.models.mutate_projects.judy import Judy


# Variables for Java and Pit
NUMBER_OF_MAVEN_FILES = 1  # Number of pom.xml each project must have
CLONED_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_repos")
PUSH_DIRECTORY = os.path.join("applications", "Mutate", "static", "index")
#  CLONED_REPOS_PATH = 'cloned_repos'
MAX_JUNIT_TESTS = 40  # maximum number of junit tests
MIN_JUNIT_TESTS = 0  # minimum number of junit tests

EXPERIMENT_RESULTS_FILE = "experiment_results.txt"


class MutateMutipleProjects(object):

    def __init__(self):
        self.languages = ["python", "java", "ruby", "c"]  # languages accepted
        self.project_storage = []  # Accepted projects array

        # For Experiment
        self.total_projects_found = 0
        self.total_projects_not_using_maven = 0
        self.total_projects_not_using_junit = 0
        self.total_projects_failing_tests = 0

    def main(self, search_terms, authentication, task, source_forge, mutation_tool):
        language = search_terms['language']
        number_of_projects = search_terms['number_of_projects']

        # Check to see if language is supported
        if language not in self.languages:
            print "DEBUG:", language, "is not supported."
            return False

        # Create directory for current user search
        current_directory = os.path.join(CLONED_REPOS_PATH, str(task))
        print "DEBUG:", "Creating task directory:", current_directory
        os.makedirs(current_directory)

        push_directory = os.path.join(PUSH_DIRECTORY, str(task))
        print "DEBUG:", "Creating push directory:", push_directory
        os.makedirs(push_directory)

        # Initialise sourceforge
        if source_forge == "Github":
            search = Github(search_terms, authentication, task, current_directory)
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
        elif mutation_tool == "judy":
            tool = Judy(None)
        else:
            # Another tool could be set up here
            # e.g.
            # tool = SomeTool(args)
            # SomeTool must extend MutationTool
            print "DEBUG:", mutation_tool, "is not supported"
            return False

        # Loop until the required amount of projects are found.
        while len(self.project_storage) < number_of_projects:
            # Add project to experiment records
            print "Writing name"
            with open(EXPERIMENT_RESULTS_FILE, 'a') as myfile:
                myfile.write(search_result+'\n')

            self.total_projects_found += 1
            print len(self.project_storage)
            requirements_met = tool.check_requirements(search, search_result)
            # If project has required fields get project from sourceforge
            if requirements_met is True:
                # Put project in project format
                current_project = Project(search.get_current_project(), source_forge)
                tool.set_current_project(current_project)
                # Get project from sourceforge
                cloned_project_path = search.clone_repo(current_project)
                # Run setup for tool
                setup_passed = tool.run_setup(cloned_project_path)
                if setup_passed is True:
                    # Run tool
                    tool_ran_successfully = tool.run(cloned_project_path)
                    # if tool ran successfully add project to storage and write to file
                    print tool_ran_successfully

                    if tool_ran_successfully is not False:
                        # raise
                        self.project_storage.append(current_project)
                        print "Appending", current_project.name, "to project_descriptors.txt"
                        with open(os.path.join(current_directory, 'project_descriptors.txt'), "a") as my_file:
                            my_file.write(str(current_project.name) + ',' +
                                          str(current_project.clone[:-4]) + ',' +
                                          str(current_project.language) + ',' +
                                          str(current_project.url) + ',' +
                                          str(current_project.size) + ',' +
                                          str(current_project.pom_location) + ',' +
                                          str(tool_ran_successfully) + '\n')
                else:
                    self.total_projects_failing_tests += 1
                    with open(EXPERIMENT_RESULTS_FILE, 'a') as myfile:
                        myfile.write("failing tests\n")
            else:
                # For Experiment
                if not requirements_met[0]:
                    self.total_projects_not_using_maven += 1
                    with open(EXPERIMENT_RESULTS_FILE, 'a') as myfile:
                        myfile.write("does not use maven\n")
                if not requirements_met[1]:
                    self.total_projects_not_using_junit += 1
                    with open(EXPERIMENT_RESULTS_FILE, 'a') as myfile:
                        myfile.write("does not use junit\n")

            with open(EXPERIMENT_RESULTS_FILE, 'a') as myfile:
                myfile.write("\n\n")
            a = open('temp_output.txt', 'w')
            a.write('total projects found: ' + str(self.total_projects_found) +
                    '\ntotal projects not using junit: ' + str(self.total_projects_not_using_junit) +
                    '\ntotal projects not using maven:' + str(self.total_projects_not_using_maven) +
                    '\ntotal projects with failing tests: ' + str(self.total_projects_failing_tests) +
                    '\ntotal projects mutation tested: ' + str(len(self.project_storage)))
            a.close()

            # Get next search result
            search_result = search.get_next_search_result()

        print "Exited for loop"
        print self.project_storage
        for project in self.project_storage:
            tool.set_current_project(project)
            tool.push_results(push_directory)
        print "DEBUG: Projects Found"
        print 'total projects found:', self.total_projects_found
        print 'total projects not using junit:', self.total_projects_not_using_junit
        print 'total projects not using maven:', self.total_projects_not_using_maven
        print 'total projects with failing tests', self.total_projects_failing_tests
        print 'total projects mutation tested', len(self.project_storage)

        return True
