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
        self.token = open(os.path.join('applications','Mutate','local_resources','token.txt'), 'r').read()
        # Clear old test files
        self.test_folder = os.path.join('applications','Mutate','models','mutate_projects','cloned_repos','test')
        self.results_test_folder = os.path.join('applications','Mutate','static','index', 'test')
        self.repo_to_delete = os.path.join('applications','Mutate','tests','repotodelete')
        if os.path.isdir(self.test_folder):
            shutil.rmtree(self.test_folder, onerror=onerror)
        if os.path.isdir(self.results_test_folder):
            shutil.rmtree(self.results_test_folder, onerror=onerror)
        if not os.path.isdir(self.repo_to_delete):
            os.makedirs(self.repo_to_delete)

    def test_main(self):
        from applications.Mutate.models.mutate_projects.main import Main
        number_of_projects = 10

        Main().main('th', 100000, 0, 'java', 'forks', 'desc', number_of_projects, 'majicmoo', self.token,
                           'test', 'Github', 'pit')
        # Check correct number of projects exist
        for i in range(1, number_of_projects):
            self.assertEquals(os.path.isdir(os.path.join(self.test_folder, str(i))), True)

        number_of_project_results = len(next(os.walk(self.results_test_folder))[1])
        self.assertEquals(number_of_projects,number_of_project_results)

    def test_functions(self):
        from applications.Mutate.models.mutate_projects.functions import Functions
        Functions().delete_repo(self.repo_to_delete)
        self.assertEquals(os.path.isdir(self.repo_to_delete), False)


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestMutateProjects))
unittest.TextTestRunner(verbosity=2).run(suite)
