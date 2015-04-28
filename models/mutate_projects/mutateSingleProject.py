import os
from applications.Mutate.models.mutate_projects.project import Project
from applications.Mutate.models.mutate_projects.github import Github
from applications.Mutate.models.mutate_projects.bitbucket import Bitbucket
from applications.Mutate.models.mutate_projects.pit import Pit
from applications.Mutate.models.mutate_projects.judy import Judy

CLONED_SINGLE_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_single_repos")
PUSH_DIRECTORY = os.path.join("applications", "Mutate", "static", "index")


class MutateSingleProject():
    def __init__(self):
        self.languages = ["python", "java", "ruby", "c"]  # languages accepted

    def main(self, search_terms, authentication, task, source_forge, mutation_tool):
        # if language not in self.languages:
        #     print "DEBUG:", language, "is not supported."
        #     return False

        # Create directory for current user search
        current_directory = os.path.join(CLONED_SINGLE_REPOS_PATH, str(task))
        print "DEBUG:", "Creating task directory:", current_directory
        os.makedirs(current_directory)

        push_directory = os.path.join(PUSH_DIRECTORY, str(task))
        print "DEBUG:", "Creating push directory:", push_directory
        os.makedirs(push_directory)

        # Initialise sourceforge
        if source_forge.lower() == "github":
            search = Github(search_terms, authentication, task, current_directory)
        elif source_forge.lower() == "bitbucket":
            search = Bitbucket(search_terms, authentication, task, current_directory)
        else:
            # Another sourceforge could be set up here
            # e.g.
            # search = Bitbucket(args)
            # search_result = search.initial_search_bitbucket()
            # bitbucket must extend SourceForge
            print "DEBUG:", source_forge, "is not supported"
            return False

        # Initialise tool
        if mutation_tool.lower() == "pit":
            tool = Pit(None)
        elif mutation_tool.lower() == "judy":
            tool = Judy(None)
        else:
            # Another tool could be set up here
            # e.g.
            # tool = SomeTool(args)
            # SomeTool must extend MutationTool
            print "DEBUG:", mutation_tool, "is not supported"
            return False
        json = search.get_single_project()
        project = Project(json, source_forge)
        cloned_project_path = search.clone_repo(project)
        tool.set_current_project(project)
        setup_passed = tool.run_setup(cloned_project_path)
        if setup_passed is True:
            # Run tool
            tool_ran_successfully = tool.run(cloned_project_path)
            # if tool ran successfully add project to storage and write to file
            print tool_ran_successfully

            print "Appending", project.name, "to project_descriptors.txt"
            with open(os.path.join(current_directory, 'project_descriptors.txt'), "a") as my_file:
                my_file.write(str(project.name) + ',' +
                              str(project.clone[:-4]) + ',' +
                              str(project.language) + ',' +
                              str(project.url) + ',' +
                              str(project.size) + ',' +
                              str(project.pom_location) + ',' +
                              str(tool_ran_successfully) + '\n')
            tool.push_results(push_directory)

        else:
            "Project is not compatible with mutation tool"