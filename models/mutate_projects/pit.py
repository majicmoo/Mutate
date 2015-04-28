from applications.Mutate.models.mutate_projects.mavenXMLConverter import ConvertXML
from applications.Mutate.models.mutate_projects.mutationTool import MutationTool
from applications.Mutate.models.mutate_projects.runMaven import RunMaven
from applications.Mutate.models.mutate_projects.project import Project
import applications.Mutate.models.mutate_projects.functions as functions
import os
import subprocess
import shutil

EXPERIMENT_RESULTS_FILE = "experiment_results.txt"

NUMBER_OF_MAVEN_FILES = 1  # Number of pom.xml each project must have
MAX_JUNIT_TESTS = 40  # maximum number of junit tests
MIN_JUNIT_TESTS = 0  # minimum number of junit tests


class Pit(MutationTool):

    def __init__(self, *args, **kwargs):
        super(Pit, self).__init__(*args, **kwargs)

    def check_requirements(self, search, search_result):
        # Check project contains maven and junit files
        search_for_mvn = search.search_for_mvn(search_result)["total_count"]
        if search_for_mvn == NUMBER_OF_MAVEN_FILES:
            search_for_junit = search.search_repo_for_junit_tests(search_result)["total_count"]
            # if search_for_junit < MAX_JUNIT_TESTS and search_for_junit > MIN_JUNIT_TESTS:
            if MIN_JUNIT_TESTS < search_for_junit < MAX_JUNIT_TESTS:
                return True
            else:
                return [True, False]
        else:
            search_for_junit = search.search_repo_for_junit_tests(search_result)["total_count"]
            if MIN_JUNIT_TESTS < search_for_junit < MAX_JUNIT_TESTS:
                return [False, True]
            return [False, False]

    def run_setup(self, project_location):
        # Run anything required to setup tool
        run_maven = RunMaven(self.project).run_maven(project_location)

        if run_maven is False:
            return False
        else:
            pom = self.find_pom(project_location)
            target_program = self.find_mutation_targets(str(pom))
            ConvertXML.convert_pom(target_program, target_program, pom)
            return True

    def run(self, current_file):
        pom = self.find_pom(current_file)
        print "DEBUG: running pit"
        try:
            command = "mvn org.pitest:pitest-maven:mutationCoverage -f " + pom
            print command
            pit_test = functions.Functions().run(600, command)
            print pit_test
            pit_test = pit_test.split('\n')
            for i in pit_test:
                if 'BUILD SUCCESS' in i:
                    print "DEBUG: Pit Passes"
                    mutation_score = self.find_mutation_score(self.find_pit_report_index(pom))
                    with open(EXPERIMENT_RESULTS_FILE, 'a') as myfile:
                        myfile.write("mutation score: " + str(mutation_score)+'\n')
                    return mutation_score
            print "DEBUG: Pit Failed"
            functions.Functions().delete_repo(current_file)
            return False
        except subprocess.CalledProcessError:
            print "DEBUG: Pit Failed"
            functions.Functions().delete_repo(current_file)
            return False

    def find_mutation_score(self, index):
        print "DEBUG: Finding Mutation Score"
        index_file = open(index, 'r')
        print "DEBUG: File Opened"
        print index
        print index_file
        index = index_file.readlines()
        index_file.close()
        for i in index:
            if '<div class="coverage_bar' in i:
                i = i.split('>')[1].split('%')[0]
                return int(i)
        return 0

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
        target = target[:-1]+'*'
        return target

    def find_pom(self, current_file):
        print "DEBUG: Locating pom.xml"
        for root, dirnames, files in os.walk(current_file):
            for i in files:
                if i == 'pom.xml':
                    self.project.pom_location = os.path.join(root, i)
                    return os.path.join(root, i)

    def push_results(self, destination):
        pom = self.project.pom_location
        pit_report_location = self.find_pit_report(pom)
        print "DEBUG: Copying index"
        shutil.copytree(pit_report_location, os.path.join(destination, self.project.name))

    def find_pit_report_index(self, pom):
        pit_reports = os.path.join(os.path.dirname(pom), 'target', 'pit-reports')
        for root, dirnames, files in os.walk(pit_reports):
            for i in files:
                if i == 'index.html':
                    return os.path.join(root, i)

    def find_pit_report(self, pom):
        pit_reports = os.path.join(os.path.dirname(pom), 'target', 'pit-reports')
        for root, dirnames, files in os.walk(pit_reports):
            for i in files:
                if i == 'index.html':
                    return root
#
# pit = Pit(Project({'clone_url': False, 'name': False, 'language': False, 'url': False, 'size': False}))
# print pit.find_mutation_targets(pit.find_pom(r'C:\Users\Megan\Documents\web2py_win\web2py\applications\Mutate\models
# \mutate_projects\cloned_repos\1\2'))
# pit.find_mutation_score(pit.find_index(pit.find_pom(r'C:\Users\Megan\Documents\web2py_win\web2py\applications\Mutat
# e\models\mutate_projects\cloned_repos\57\1')))