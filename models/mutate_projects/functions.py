import shutil
import os
import subprocess
import threading


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

class Functions(object):

    def __init__(self):
        self.output = None
        self.process = None

    @staticmethod
    def delete_repo(current_file):
        print "DEBUG: Deleting", current_file
        shutil.rmtree(current_file, onerror=onerror)

    def run(self, timeout, cmd):
        self.output = None
        self.process = None
        timeout = float(timeout)
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            temp = self.process.communicate()
            self.output = temp[0]
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process : TIMEOUT'
            self.process.terminate()

            thread.join()
            print 'terminated'

        return self.output