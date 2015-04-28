
class Project(object):

    def __init__(self, project, format):

        self.project_dictionary = project

        if format.lower() == "github":
            self.clone = project["clone_url"]
            self.url = project["url"]
            self.type = "git"
        elif format.lower() == "bitbucket":
            self.clone = project['links']['clone'][0]['href']
            self.url = project['links']['html']
            self.type = project['scm']

        self.name = project["name"]
        self.language = project["language"]
        self.size = project["size"]
        self.src = None
        self.classpath = ""
        self.main = ""
        self.pom_location = None