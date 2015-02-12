__author__ = 'Megan'
import subprocess
import os


class CloneProject(object):

    def __init__(self, path_cloned_repos, project):
        self.path_cloned_repos = path_cloned_repos
        self.project = project

    def clone_repo(self):
        # create folder to clone into
        max_file_number = 0
        for files in os.walk(self.path_cloned_repos):
            temp = map(int, files[1])
            if len(temp) > 0:
                max_file_number = max(temp)
            break
        print "DEBUG: Make directory: " + self.path_cloned_repos+os.sep+str(max_file_number+1)

        os.makedirs(self.path_cloned_repos+os.sep+str(max_file_number+1))
        print self.path_cloned_repos+os.sep+str(max_file_number+1)
        # clone repo
        print "DEBUG: Cloning", self.project.name, "into", self.path_cloned_repos+os.sep+str(max_file_number+1)
        subprocess.call("git clone "+self.project.clone+" "+self.path_cloned_repos+os.sep+str(max_file_number+1),
                        shell=True)
        return self.path_cloned_repos+os.sep+str(max_file_number+1)
