import subprocess
import shutil
import os


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


class RunMaven(object):

    def __init__(self, project):
        self.project = project

    def run_maven(self, current_file):
        pom = self.find_pom(current_file)
        print "DEBUG: Running tests for ", current_file
        print "mvn -f " + str(pom) + " test"
        # check output if mvn tests fail delete folder
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

    def delete_repo(self, current_file):
        print "DEBUG: Deleting", current_file
        shutil.rmtree(current_file, onerror=onerror)