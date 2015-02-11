__author__ = 'Megan'
from applications.Mutate.models.testinggithubapi.mavenXMLConverter import ConvertXML
import os
import subprocess


class Pit(object):

    def __init__(self):
        pass

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

    def run(self, current_file, pom):
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
            return False
        except subprocess.CalledProcessError:
            print "DEBUG: Pit Failed"
            return False