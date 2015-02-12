__author__ = 'Megan'
import os
import requests
import time
import subprocess
from applications.Mutate.models.mutate_projects.project import Project


GITHUB_API = 'https://api.github.com'
MAX_ITEMS = 30  # max number of items on each page in github
SLEEP_TIME = 60  # Time between API accesses when reached rate limit
ACCEPTED_STATUS_CODE = 200  # Status code of successful access to API
NUMBER_OF_MAVEN_FILES = 1  # How many maven files you wish to find
CLONED_REPOS_PATH = os.path.join("applications", "Mutate" ,"models" , "mutate_projects" ,"cloned_repos")
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

    def initial_search(self):
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

    def clone_repo(self, project):
        # create folder to clone into
        max_file_number = 0
        for files in os.walk(CLONED_REPOS_PATH):
            temp = map(int, files[1])
            if len(temp) > 0:
                max_file_number = max(temp)
            break
        print "DEBUG: Make directory: " + CLONED_REPOS_PATH+os.sep+str(max_file_number+1)
        os.makedirs(CLONED_REPOS_PATH+os.sep+str(max_file_number+1))
        print CLONED_REPOS_PATH+os.sep+str(max_file_number+1)
        # clone repo
        print "DEBUG: Cloning", project.name, "into", CLONED_REPOS_PATH +os.sep+str(max_file_number+1)
        subprocess.call("git clone "+project.clone+" "+CLONED_REPOS_PATH+os.sep+str(max_file_number+1),
                        shell=True)
        return CLONED_REPOS_PATH+os.sep+str(max_file_number+1)

    def search_repo_for_junit_tests(self, repo):
        # search repository (given by repo) for junit tests
        search_string = self.create_search_in_file_type_in_repo_url(repo, "junit")
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

    def create_search_in_file_type_in_repo_url(self, repo, keyword):
        # Create URL to search for a keyword in a file type in a repo, eg. junit in java files
        start = "https://api.github.com/search/code"
        keyword = "?q="+keyword
        language_search = "language:"+self.language
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