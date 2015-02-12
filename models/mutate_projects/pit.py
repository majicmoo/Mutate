from applications.Mutate.models.mutate_projects.mavenXMLConverter import ConvertXML
from applications.Mutate.models.mutate_projects.mutationTool import MutationTool
from applications.Mutate.models.mutate_projects.runMaven import RunMaven
from applications.Mutate.models.mutate_projects.project import Project
import os
import subprocess


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
                return False
        else:
            return False

    def run_setup(self, project_location):
        # Run anything required to setup tool
        return RunMaven(self.project).run_maven(project_location)

    def run(self, current_file):
        pom = self.find_pom(current_file)
        target_program = self.find_mutation_targets(str(pom))
        ConvertXML.convert_pom(target_program, target_program, pom)
        print "DEBUG: running pit"
        try:
            print os.getcwd()
            print "mvn org.pitest:pitest-maven:mutationCoverage -f " + pom
            pit_test = subprocess.check_output("mvn org.pitest:pitest-maven:mutationCoverage -f " + pom, shell=True)
            pit_test = pit_test.split('\n')
            for i in pit_test:
                if 'BUILD SUCCESS' in i:
                    print "DEBUG: Pit Passes"
                    return True
            print "DEBUG: Pit Failed"
            return False
        except subprocess.CalledProcessError:
            print "DEBUG: Pit Failed"
            return False

    def find_mutation_targets(self, pom):
        directory = os.path.dirname(pom)
        test = os.path.join(directory, 'src', 'test')
        target = ""
        for root, dirnames, files in os.walk(test):
            if len(dirnames) == 1:
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
                    self.project.pom_location = root+os.sep+i
                    return os.path.join(root,i)

#
# pit = Pit(Project({'clone_url': False, 'name': False, 'language': False, 'url': False, 'size': False}))
# print pit.find_mutation_targets(pit.find_pom('/usr/userfs/m/mep513/Documents/iapt/web2py/applications/Mutate/models/mutate_projects/cloned_repos/23/1'))
