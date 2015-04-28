from applications.Mutate.models.mutate_projects.mavenXMLConverter import ConvertXML
from applications.Mutate.models.mutate_projects.mutationTool import MutationTool
from applications.Mutate.models.mutate_projects.runMaven import RunMaven
from applications.Mutate.models.mutate_projects.project import Project
import applications.Mutate.models.mutate_projects.functions as functions
import os
import subprocess
import shutil
import time

NUMBER_OF_POM_FILES = 1
MIN_JUNIT_TESTS = 1
MAX_JUNIT_TESTS = 40
JUDY_PATH = os.path.join("applications", "Mutate", "models", "mutate_projects", "judy")

class Judy(MutationTool):

    def __init__(self, *args, **kwargs):
        super(Judy, self).__init__(*args, **kwargs)
        self.target_program = None

    def check_requirements(self, search, search_result):
        # Check project contains ant and junit files
        search_for_maven = search.search_for_mvn(search_result)["total_count"]
        if search_for_maven == NUMBER_OF_POM_FILES:
            search_for_junit = search.search_repo_for_junit_tests(search_result)["total_count"]
            if MIN_JUNIT_TESTS < search_for_junit < MAX_JUNIT_TESTS:
                return True
            else:
                return False
        else:
            return False

    def run_setup(self, project_location):
        # Run anything required to setup tool
        run_maven = RunMaven(self.project).run_maven(project_location)
        if run_maven is False:
            return False
        else:
            pom = self.find_pom(project_location)
            self.target_program = self.find_mutation_targets(str(pom))
            ConvertXML.convert_pom_judy(self.target_program, self.target_program, pom)
            return True
        pass

    def run(self, current_file):
        # Run Mutation Tool
        pom = self.find_pom(current_file)
        print "DEBUG: running judy"
        try:
            command = "java -jar "+ os.path.join(JUDY_PATH,"judy-2.1.0.jar")+ " -w " + self.target_program + " -c main"+\
                      os.sep+self.target_program+os.sep+"*"+" -t test"+os.sep+ self.target_program+os.sep+"*"
            print command
            #judy_test = functions.Functions().run(600, command)
            judy_test = subprocess.check_output(command, shell=True)
            print judy_test
            judy_test = judy_test.split('\n')
            for i in judy_test:
                if 'BUILD SUCCESS' in i:
                    print "DEBUG: judy Passes"
            print "DEBUG: judy Failed"
            functions.Functions().delete_repo(current_file)
            return False
        except subprocess.CalledProcessError:
            time.sleep(30)
            print "DEBUG: judy Failed"
            functions.Functions().delete_repo(current_file)
            return False

    def set_current_project(self, current_project):
        self.project = current_project

    def push_results(self, destination):
        pass

    def find_mutation_targets(self, pom):
        directory = os.path.dirname(pom)
        test = os.path.join(directory, 'src', 'test')
        target = ""
        start_string = False
        for root, dirnames, files in os.walk(test):
            if len(dirnames) == 1:
                if str(dirnames[0]) != 'java':
                    start_string = True
                    target += str(dirnames[0])
                    print dirnames
                elif start_string is True:
                    target += str(dirnames[0])
                    print dirnames
            else:
                if target != "":
                    break
            if target != "":
                target += "."
        target = target[:-1]
        return target

    def find_pom(self, current_file):
        print "DEBUG: Locating pom.xml"
        for root, dirnames, files in os.walk(current_file):
            for i in files:
                if i == 'pom.xml':
                    self.project.pom_location = os.path.join(root, i)
                    return os.path.join(root, i)
