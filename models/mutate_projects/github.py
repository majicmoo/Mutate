__author__ = 'Megan'
import os
import requests
import time
import subprocess
from applications.Mutate.models.mutate_projects.project import Project
from applications.Mutate.models.mutate_projects.sourceForge import SourceForge


GITHUB_API = 'https://api.github.com'
MAX_ITEMS = 30  # max number of items on each page in github
SLEEP_TIME = 60  # Time between API accesses when reached rate limit
ACCEPTED_STATUS_CODE = 200  # Status code of successful access to API
NUMBER_OF_MAVEN_FILES = 1  # How many maven files you wish to find
MAX_JUNIT_TESTS = 40
MIN_JUNIT_TESTS = 0


class Github(SourceForge):

    def __init__(self, keyword, maxsize, minsize, language, sort_by, order_by, username, token, task):
        super(Github, self).__init__(keyword, maxsize, minsize, language, sort_by, order_by, username, token, task)
        self.count_github_access = 0
        self.pagination = 2
        self.search_counter = 0
        self.search_string = ""
        self.search_dictionary = None
        self.cloned_repos_path = os.path.join("applications", "Mutate" ,"models" , "mutate_projects" ,"cloned_repos", str(self.task))

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
        print "Current Path:",self.cloned_repos_path
        for files in os.walk(self.cloned_repos_path):
            temp = map(int, files[1])
            print temp
            if len(temp) > 0:
                max_file_number = max(temp)
            break
        print "Max file number:", max_file_number
        new_directory = os.path.join(self.cloned_repos_path,str(max_file_number+1))

        print "DEBUG: Make directory: " + new_directory
        os.makedirs(new_directory)
        # clone repo
        print "DEBUG: Cloning", project.name, "into", new_directory
        subprocess.call("git clone "+project.clone+" "+new_directory,
                        shell=True)
        return new_directory

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
        sort = "sort=" + self.sort_by
        order = "order=" + self.order_by
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