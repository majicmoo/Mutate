import unittest
import os
import shutil


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


class TestMutateProjects(unittest.TestCase):
    def setUp(self):
        # Get Token
        self.token = open(os.path.join('applications', 'Mutate', 'local_resources', 'token.txt'), 'r').read()
        # Clear old test files
        self.test_folder = os.path.join('applications', 'Mutate', 'models', 'mutate_projects', 'cloned_repos', 'test')
        self.results_test_folder = os.path.join('applications', 'Mutate', 'static', 'index', 'test')
        self.repo_to_delete = os.path.join('applications', 'Mutate', 'tests', 'repotodelete')
        if os.path.isdir(self.test_folder):
            shutil.rmtree(self.test_folder, onerror=onerror)
        if os.path.isdir(self.results_test_folder):

            shutil.rmtree(self.results_test_folder, onerror=onerror)
        if not os.path.isdir(self.repo_to_delete):
            os.makedirs(self.repo_to_delete)
        print "creating results"

    def test_mutatesingleproject(self):
        from applications.Mutate.models.mutate_projects.mutateSingleProject import MutateSingleProject
        search_terms = {}
        # Set others to False
        search_terms['team_name'] = 'traackr'
        search_terms['repo_name'] = 'test-maven-git-flow'
        # Search Terms
        search_terms['keyword'] = False
        search_terms['maxsize'] = False
        search_terms['minsize'] = False
        search_terms['language'] = False
        search_terms['sortby'] = False
        search_terms['orderby'] = False
        search_terms['number_of_projects'] = False

        authentication = {}
        authentication['username'] = False
        authentication['token'] = False

        MutateSingleProject().main(search_terms, authentication, "test", "Bitbucket", "pit")

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestMutateProjects))
unittest.TextTestRunner(verbosity=2).run(suite)
