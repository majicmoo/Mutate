
class Project(object):

    def __init__(self, project):
        self.project_dictionary = project
        self.clone = project["clone_url"]
        self.name = project["name"]
        self.language = project["language"]
        self.url = project["url"]
        self.size = project["size"]
        self.src = None
        self.classpath = ""
        self.main = ""
        self.pom_location = None



