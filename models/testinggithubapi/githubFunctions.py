__author__ = 'Megan'
import os
import requests
import time

from applications.Mutate.models.testinggithubapi.project import Project


GITHUB_API = 'https://api.github.com'
MAX_ITEMS = 30  # max number of items on each page in github
SLEEP_TIME = 60  # Time between API accesses when reached rate limit
ACCEPTED_STATUS_CODE = 200  # Status code of successful access to API
NUMBER_OF_MAVEN_FILES = 1  # How many maven files you wish to find
CLONED_REPOS_PATH = os.path.join("applications", "Mutate" ,"models" , "testinggithubapi" ,"clonedrepos")
MAX_JUNIT_TESTS = 40
MIN_JUNIT_TESTS = 0


class GithubFunctions(object):

    def __init__(self, keyword, maxsize, minsize, language, sortby,
                      orderby, username, token, task):
        self.count_github_access = 0
        self.keyword = keyword
        self.maxsize = maxsize
        self.minsize = minsize
        self.language = language
        self.sortby = sortby
        self.orderby = orderby
        self.username = username
        self.token = token
        self.task = task
        self.pagination = 2
        self.search_counter = 0
        self.search_string = ""
        self.search_dictionary = None


    def initial_search_github(self):
        # create search url
        self.search_string = self.create_general_search_url()
        self.search_dictionary = self.request_github(self.search_string)
        return self.search_dictionary["items"][self.search_counter]["full_name"]


    def get_next_search_result(self):
        self.search_counter += 1
        if self.search_counter >= MAX_ITEMS:
            self.search_dictionary = self.request_github(self.search_string+'&page='+str(self.pagination))
            self.pagination += 1
            self.search_counter = 0
        return self.search_dictionary["items"][self.search_counter]["full_name"]

    def get_current_project(self):
        return self.search_dictionary["items"][self.search_counter]




    def search_github(self):
        # keyword: search keyword
        # maxsize: maximum size of repository
        # minsize: minimum size of repository
        # language: main language of repository
        # sortby: what you want to sort repos by (stars /forks / updated)
        # orderby: order sort by ascending or descending (asc/desc)



        # create search url
        search_string = self.create_general_search_url(keyword, language, sortby, orderby, minsize, maxsize)
        search_dictionary = self.request_github(search_string, username, token)

        # Search through found repository's and see if they contain files which contain junit
        # If they do store to repository_storage
        pagination = 2
        repository_storage = []
        search_counter = 0
        while len(repository_storage) < self.number_of_projects:
            print search_counter
            if search_counter >= MAX_ITEMS:
                search_dictionary = self.request_github(search_string+'&page='+str(pagination))
                pagination += 1

            repo_name = search_dictionary["items"][search_counter]["full_name"]
            #If pit and java
            if self.language == "java":
                #Java is language
                if self.mutation_tool == "pit":
                    # Pit is mutation tool
                    search_for_mvn = self.search_for_mvn(repo_name)["total_count"]
                    if search_for_mvn == NUMBER_OF_MAVEN_FILES:
                        search_for_junit = self.search_repo_for_junit_tests(repo_name)["total_count"]
                        if search_for_junit < MAX_JUNIT_TESTS and search_for_junit > MIN_JUNIT_TESTS:
                            temp_project = Project(search_dictionary["items"][search_counter])
                            print "*******************************************"
                            if RunMutationTools(temp_project, cloned_path).setup_repo("pit"):
                                print "*******************************************"
                                repository_storage.append(temp_project)
                                # Add repository to database
                                print "Appending", temp_project.name, "to project descriptors file"
                                with open(CLONED_REPOS_PATH + os.sep + str(self.task) + os.sep + 'projectdescriptors.txt', "a") as myfile:
                                    myfile.write(str(temp_project.name) + '\n' +
                                                 str(temp_project.clone[:-4]) + '\n' +
                                                 str(temp_project.language) + '\n' +
                                                 str(temp_project.url) + '\n' +
                                                 str(temp_project.size) + '\n' +
                                                 str(temp_project.pom_location) + '\n')
                    search_counter += 1
                    # print "PAGE NUMBER:", pagination
                    # print "ENDED ON:", search_string+'&page='+str(pagination)
                else:
                    print "DEBUG", self.mutation_tool, "is not currently supported."
            else:
                print "DEBUG", self.language, "is not currently supported."
        return repository_storage

    def search_repo_for_junit_tests(self, repo):
        # search repository (given by repo) for junit tests
        search_string = self.create_search_in_file_type_in_repo_url(language, repo, "junit")
        return self.request_github(search_string)

    def search_for_mvn(self, repo):
        # search repo for pom.xml file
        search_string = self.create_file_in_project_search_url('xml+pom', repo)
        return self.request_github(search_string)

    def create_general_search_url(self):
        # Search github using keyword and language
        start = GITHUB_API + '/search/repositories?'
        search_keyword = "q=" + self.keyword
        search_language = 'language:' + self.language
        sort = "sort=" + self.sortby
        order = "order=" + self.orderby
        size = "size:" + str(self.minsize) + ".." + str(self.maxsize)
        # Search for projects
        return start + search_keyword + "+" + size + "+" + search_language + "&" + sort + "&" + order

    def create_file_in_project_search_url(self, filename, repo):
        # Create URL to search for a file in a project
        start = "https://api.github.com/search/code?q=project+"
        filename = "filename:."+filename
        repo_search = "+repo:"+repo
        return start + filename + repo_search

    def create_search_in_file_type_in_repo_url(self, language, repo, keyword):
        # Create URL to search for a keyword in a file type in a repo, eg. junit in java files
        start = "https://api.github.com/search/code"
        keyword = "?q="+keyword
        language_search = "language:"+language
        repo_search = "+repo:"+repo
        return start + keyword + "+in:file+" + language_search + repo_search

    def sleep_search(self):
        print "DEBUG sleep:", SLEEP_TIME, "seconds"
        time.sleep(SLEEP_TIME)

    def request_github(self, search_string):
        while True:
            print 'DEBUG: requesting', search_string
            github_request = requests.get(search_string, auth=(self.username+"/token", self.token))
            if github_request.status_code == ACCEPTED_STATUS_CODE:
                return github_request.json()
            else:
                self.sleep_search()
                continue