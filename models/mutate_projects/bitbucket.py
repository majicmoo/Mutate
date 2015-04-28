from applications.Mutate.models.mutate_projects.sourceForge import SourceForge
import os
import requests
from requests.exceptions import ConnectionError
import subprocess

BITBUCKET_API = 'https://api.bitbucket.org/2.0/'
ACCEPTED_STATUS_CODE = 200


class Bitbucket(SourceForge):
    def __init__(self, *args, **kwargs):
        super(Bitbucket, self).__init__(*args, **kwargs)

    def get_single_project(self):
        search_string = BITBUCKET_API + 'repositories' + '/' + self.team_name + '/' + self.repo_name
        json = self.request_bitbucket(search_string)
        return json

    def clone_repo(self, project):
        # create folder to clone into
        max_file_number = 0
        print "Current Path:", self.clone_repo_path
        for files in os.walk(self.clone_repo_path):
            temp = map(int, files[1])
            print temp
            if len(temp) > 0:
                max_file_number = max(temp)
            break
        print "Max file number:", max_file_number
        new_directory = os.path.join(self.clone_repo_path, str(max_file_number+1))

        print "DEBUG: Make directory: " + new_directory
        os.makedirs(new_directory)
        # clone repo
        print "DEBUG: Cloning", project.name, "into", new_directory
        subprocess.call(project.type + " clone " + project.clone + " " + new_directory, shell=True)
        return new_directory

    def request_bitbucket(self, search_string):
        while True:
            while True:
                try:
                    print 'DEBUG: requesting', search_string
                    bitbucket_request = requests.get(search_string)
                    if bitbucket_request.status_code == ACCEPTED_STATUS_CODE:
                        return bitbucket_request.json()
                except ConnectionError:
                    print 'DEBUG: Bitbucket slow to respond'
                    continue
            else:
                self.sleep_search()
                continue