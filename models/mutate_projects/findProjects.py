import time
import requests
import os


GITHUB_API = 'https://api.github.com'
MAX_ITEMS = 30  # max number of items on each page in github
SLEEP_TIME = 60  # Time between API accesses when reached rate limit
ACCEPTED_STATUS_CODE = 200  # Status code of successful access to API
NUMBER_OF_MAVEN_FILES = 1  # How many maven files you wish to find
CLONED_REPOS_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "cloned_repos")
MAX_JUNIT_TESTS = 40
MIN_JUNIT_TESTS = 0


from gluon import current
db = current.globalenv['db']

from applications.Mutate.models.mutate_projects.runMutationTools import RunMutationTools
from applications.Mutate.models.mutate_projects.project import Project
from applications.Mutate.models.mutate_projects.githubFunctions import GithubFunctions
from applications.Mutate.models.mutate_projects.cloneProject import CloneProject
from applications.Mutate.models.mutate_projects.runMaven import RunMaven
from applications.Mutate.models.mutate_projects.pit import Pit


class FindProjects(object):

    def __init__(self):
        # languages accepted
        self.languages = ["python", "java", "ruby", "c"]
        self.project_storage = []
        self.get_project = False

    def search_for_projects(self, keyword, maxsize, minsize, language, sortby, orderby, number_of_projects, username,
                            token, task, source_forge, mutation_tool):

        if language not in self.languages:
            print "DEBUG:", language, "is not supported."
            return False

        # Initialise search depending on repository
        if source_forge == "Github":
            search = GithubFunctions(keyword, maxsize, minsize, language, sortby, orderby, username, token, task)
            search_result = search.initial_search()
        else:
            print "DEBUG:", source_forge, "is not supported"
            return False

        # create directory for current user search
        os.makedirs(CLONED_REPOS_PATH + os.sep + str(task))
        cloned_path = CLONED_REPOS_PATH + os.sep + str(task)

        while len(self.project_storage) < number_of_projects:
            tool_ran_successfully = False
            # Check current project has required files
            if language == "java":
                # check for junit tests
                if source_forge == "Github":
                    search_for_mvn = search.search_for_mvn(search_result)["total_count"]
                    if search_for_mvn == NUMBER_OF_MAVEN_FILES:
                        search_for_junit = search.search_repo_for_junit_tests(search_result)["total_count"]
                        if search_for_junit < MAX_JUNIT_TESTS and search_for_junit > MIN_JUNIT_TESTS:
                            self.get_project = True

            # If project has required fields
            if self.get_project:
                # Put project in project format
                current_project = Project(search.get_current_project())
                if source_forge == "Github":
                    # clone project
                    cloned_project_path = CloneProject(cloned_path, current_project).clone_repo()
                else:
                    print "DEBUG:", source_forge, "is not supported"
                    return False

                if language == "java":
                    # run maven
                    run_maven = RunMaven(current_project).run_maven(cloned_project_path)
                    if run_maven:
                        if mutation_tool == "pit":
                            # run pit
                            tool_ran_successfully = Pit().run(RunMaven(current_project).find_pom(cloned_project_path))
                else:
                    print "DEBUG:", language, "is not supported"

                # if tool ran succesfully add project to storage and write to file
                if tool_ran_successfully:
                    self.project_storage.append(current_project)
                    print "Appending", current_project.name, "to project descriptors file"
                    with open(CLONED_REPOS_PATH + os.sep + str(task) + os.sep + 'projectdescriptors.txt', "a") as myfile:
                        myfile.write(str(current_project.name) + '\n' +
                                     str(current_project.clone[:-4]) + '\n' +
                                     str(current_project.language) + '\n' +
                                     str(current_project.url) + '\n' +
                                     str(current_project.size) + '\n' +
                                     str(current_project.pom_location) + '\n')

            if source_forge == "Github":
                search_result = search.get_next_search_result()



                                    







    def search_github(self, keyword, maxsize, minsize, language, sortby,
                      orderby, number_of_projects, username, token, task):

        # keyword: search keyword
        # maxsize: maximum size of repository
        # minsize: minimum size of repository
        # language: main language of repository
        # sortby: what you want to sort repos by (stars /forks / updated)
        # orderby: order sort by ascending or descending (asc/desc)

        if language not in self.languages:
            # Check language is valid
            print "DEBUG: language", language, "is not valid"
            return False

        # create directory for current user search
        os.makedirs(CLONED_REPOS_PATH + os.sep + str(task))
        cloned_path = CLONED_REPOS_PATH + os.sep + str(task)

        # create search url
        start = GITHUB_API + '/search/repositories?'
        search_keyword = "q=" + keyword
        search_language = 'language:' + language
        sort = "sort=" + sortby
        order = "order=" + orderby
        size = "size:" + str(minsize) + ".." + str(maxsize)
        pagination = 2
        # Search for projects
        search_string = start + search_keyword + "+" + size + "+" + search_language + "&" + sort + "&" + order
        # store dictionary of results from search inquiry
        while True:
            temp = requests.get(search_string, auth=(username+"/token", token))
            # print 'DEBUG: Status',temp.status_code
            if temp.status_code == ACCEPTED_STATUS_CODE:
                print "DEBUG: Requesting", search_string
                # search_dico = json.load(requests.get(search_string, auth=token).json())
                search_dico = temp.json()
                break
            else:
                print "DEBUG: sleep", SLEEP_TIME, "seconds"
                time.sleep(SLEEP_TIME)
                continue
        # search through found repository's and see if they contain files which contain junit
        # If they do store to repository_storage
        repository_storage = []
        search_counter = 0
        # print len(search_dico["items"])
        while len(repository_storage) < number_of_projects:
            print search_counter
            if search_counter >= MAX_ITEMS:
                # print "REACH MAX SEARCHS PAGE+1"
                while True:
                    temp = requests.get(search_string+'&page='+str(pagination), auth=(username+"/token", token))
                    # print 'DEBUG: Status',temp.status_code
                    if temp.status_code == ACCEPTED_STATUS_CODE:
                        search_dico = temp.json()
                        pagination += 1
                        search_counter = 0
                        break
                    else:
                        print "DEBUG sleep:", SLEEP_TIME, "seconds"
                        time.sleep(SLEEP_TIME)
                        continue
            # print search_counter
            repo_name = search_dico["items"][search_counter]["full_name"]

            search_for_mvn = self.search_for_mvn(repo_name, username, token)["total_count"]
            if search_for_mvn == NUMBER_OF_MAVEN_FILES:
                search_for_junit = self.search_repo_for_junit_tests(repo_name, "java", username,
                                                                    token)["total_count"]
                if search_for_junit < MAX_JUNIT_TESTS and search_for_junit > MIN_JUNIT_TESTS:
                    temp_project = Project(search_dico["items"][search_counter])
                    print "*******************************************"
                    if RunMutationTools(temp_project, cloned_path).setup_repo("pit"):
                        print "*******************************************"
                        repository_storage.append(temp_project)
                        # Add repository to database
                        print "Appending", temp_project.name, "to project descriptors file"
                        with open(CLONED_REPOS_PATH + os.sep + str(task) + os.sep + 'projectdescriptors.txt', "a") as myfile:
                            myfile.write(str(temp_project.name) + '\n' +
                                         str(temp_project.clone[:-4]) + '\n' +
                                         str(temp_project.language) + '\n' +
                                         str(temp_project.url) + '\n' +
                                         str(temp_project.size) + '\n' +
                                         str(temp_project.pom_location) + '\n')
            search_counter += 1
            # print "PAGE NUMBER:", pagination
            # print "ENDED ON:", search_string+'&page='+str(pagination)
        return repository_storage

    def search_repo_for_junit_tests(self, repo, language, username, token):
        # search repository (given by repo) for junit tests
        start = "https://api.github.com/search/code"
        keyword = "?q=junit"
        language_search = "language:"+language
        repo_search = "+repo:"+repo
        search_string = start + keyword + "+in:file+" + language_search + repo_search

        while True:
            print 'DEBUG: requesting', search_string
            temp = requests.get(search_string, auth=(username+"/token", token))
            # print 'status code', temp.status_code
            if temp.status_code == ACCEPTED_STATUS_CODE:
                return temp.json()
            else:
                print "DEBUG sleep:", SLEEP_TIME, "seconds"
                time.sleep(SLEEP_TIME)
                continue

    def search_for_mvn(self, repo, username, token):
        start = "https://api.github.com/search/code?q=project+"
        filename = "filename:.xml+pom"
        repo_search = "+repo:"+repo
        search_string = start + filename + repo_search

        while True:
            print 'DEBUG: requesting', search_string
            temp = requests.get(search_string, auth=(username+"/token", token))
            # print 'status code', temp.status_code
            if temp.status_code == ACCEPTED_STATUS_CODE:
                return temp.json()
            else:
                print "DEBUG sleep:", SLEEP_TIME, "seconds"
                time.sleep(SLEEP_TIME)
                continue