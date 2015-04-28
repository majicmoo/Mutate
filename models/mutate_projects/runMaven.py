import subprocess
import os
from applications.Mutate.models.mutate_projects.functions import Functions
import time


class RunMaven(object):

    def __init__(self, project):
        self.project = project

    def run_maven(self, current_file):
        pom = self.find_pom(current_file)
        if pom is None:
            print "DEBUG: Pom.xml not found."
            return False
        print "DEBUG: Running tests for ", current_file
        print
        # check output if mvn tests fail delete folder
        try:
            command = "mvn -f " + str(pom) + " test"
            print command
            maven_output = Functions().run(300, command)
            print maven_output
            if maven_output is not None:
                maven_output = maven_output.split("\n")
                num = '1234567890'
                tests_run, failures, errors, skipped = 0, 0, 0, 0
                for line in maven_output:
                    if "Tests run:" in line:
                        line = line.split(",")
                        tests_run, failures, errors, skipped = int("".join([c for c in line[0] if c in num])),\
                                                               int("".join([c for c in line[1] if c in num])),\
                                                               int("".join([c for c in line[2] if c in num])),\
                                                               int("".join([c for c in line[3] if c in num]))
                print "Tests run:", tests_run, "\n", "Failures:", failures, "\n", "Errors:", errors, "\n",\
                    "Skipped:", skipped

                if tests_run == 0:
                    print "DEBUG: No tests run"
                    Functions().delete_repo(current_file)
                    return False

                if failures > 0:
                    print "DEBUG: Test suite not green"
                    Functions().delete_repo(current_file)
                    return False

                print "DEBUG: Test Successful"
                return True
            else:
                print "DEBUG: Timeout"
                Functions().delete_repo(current_file)
                return False

        except subprocess.CalledProcessError:
            print "DEBUG: Test Failed"
            Functions().delete_repo(current_file)
            return False

    def find_pom(self, current_file):
        print "DEBUG: Locating pom.xml"
        print current_file
        for root, dirnames, files in os.walk(current_file):
            for i in files:
                if i == 'pom.xml':
                    self.project.pom_location = os.path.join(root, i)
                    return self.project.pom_location

