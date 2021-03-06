import os
import subprocess
import shutil
import stat  # needed for file stat
import sys
from applications.Mutate.models.mutate_projects.mavenXMLConverter import ConvertXML
from applications.Mutate.models.mutate_projects.pit import Pit

# from applications.Mutate.models.mutate_projects.project import Project


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


class RunMutationTools(object):

    def __init__(self, project, path_cloned_repos):
        self.project = project
        self.path_cloned_repos = path_cloned_repos

    def delete_repo(self, current_file):
        print "DEBUG: Deleting", current_file
        shutil.rmtree(current_file, onerror=onerror)

        # if 'win' in str(sys.platform):
        #     shutil.rmtree(os.path.join(os.getcwd(),current_file), onerror=onerror)
        # else:
        #     shutil.rmtree(current_file, onerror=onerror)


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

    def run_mvn(self, current_file):
        pom = self.find_pom(current_file)
        print "DEBUG: Running tests for ", current_file
        print "mvn -f " + str(pom) + " test"
        # checkoutput if mvn tests fail delete folder
        try:
            temp = subprocess.check_output("mvn -f " + pom + " test", shell=True)
            temp = temp.split("\n")
            num = '1234567890'
            tests_run, failures, errors, skipped = 0, 0, 0, 0
            for i in temp:
                if "Tests run:" in i:
                    i = i.split(",")
                    tests_run, failures, errors, skipped = int("".join([c for c in i[0] if c in num])),\
                                                           int("".join([c for c in i[1] if c in num])),\
                                                           int("".join([c for c in i[2] if c in num])),\
                                                           int("".join([c for c in i[3] if c in num]))
            print "Tests run:", tests_run, "\n", "Failures:", failures, "\n", "Errors:", errors, "\n", \
                "Skipped:", skipped

            if tests_run == 0:
                print "DEBUG: No tests run"
                self.delete_repo(current_file)

            if failures > 0:
                print "DEBUG: Test suite not green"
                self.delete_repo(current_file)

            print "DEBUG: Test Successful"
            return True
        except subprocess.CalledProcessError:
            print "DEBUG: Test Failed"
            self.delete_repo(current_file)
            return False

    def find_pom(self, current_file):
        print "DEBUG: Locating pom.xml"
        for root, dirnames, files in os.walk(current_file):
            for i in files:
                if i == 'pom.xml':
                    self.project.pom_location = root+os.sep+i
                    return root+os.sep+i

    def find_mutation_targets(self, pom):
        directory = os.path.dirname(pom)
        test = directory + os.sep + 'src' + os.sep + 'test'
        for root, dirnames, files in os.walk(test):
            for i in files:
                test = root
        file_list = []
        for i in test.split('\\'):
            for j in i.split('/'):
                file_list.append(j)
        print file_list
        after_java = False
        test = ""
        for i in file_list:
            if after_java:
                test += i+"."
            if str(i) == 'java':
                after_java = True
        test = test[:-1]+'*'
        return test

    def run_pit(self, current_file):
        pom = self.find_pom(current_file)
        target_program = self.find_mutation_targets(str(pom))
        xml_converter = ConvertXML()
        xml_converter.convert_pom(target_program, target_program, pom)
        print "DEBUG: running pit"
        try:
            print os.getcwd()
            print "mvn org.pitest:pitest-maven:mutationCoverage -f " + pom
            pittest = subprocess.check_output("mvn org.pitest:pitest-maven:mutationCoverage -f " + pom, shell=True)
            pittest = pittest.split('\n')
            for i in pittest:
                if 'BUILD SUCCESS' in i:
                    return True
            print "DEBUG: Pit Failed"
            self.delete_repo(current_file)
            return False
        except subprocess.CalledProcessError:
            print "DEBUG: Pit Failed"
            self.delete_repo(current_file)
            return False

    def setup_repo(self, mutation_tool_name):
        # Clone repo
        current_file = self.clone_repo()
        # run tests
        print "*******************************************"
        if self.run_mvn(str(current_file)):
            if str(mutation_tool_name) == "pit":
                return self.run_pit(str(current_file))
        else:
            return False

    def temp(self, mutation_tool_name):
        # Clone repo
        current_file = self.clone_repo()
        pom = self.find_pom(current_file)
        # run tests
        print "*******************************************"
        if self.run_mvn(str(current_file)):
            if str(mutation_tool_name) == "pit":
                pit = Pit()
                if not pit.run(str(current_file), pom):
                    self.delete_repo(current_file)
                else:
                    return True
        else:
            return False