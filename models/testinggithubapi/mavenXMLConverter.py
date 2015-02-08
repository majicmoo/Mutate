__author__ = 'Megan'

import xml.etree.ElementTree as ElementTree

POM_NS = "{http://maven.apache.org/POM/4.0.0}"
LATEST_PIT_VERSION = "1.1.2"

ElementTree.register_namespace("", "http://maven.apache.org/POM/4.0.0")


class ConvertXML(object):

    def __init__(self):
        pass

    def convert_pom(self, mutate, test, pom):

        tree = ElementTree.parse(pom)
        root = tree.getroot()

        # Update Junit
        junit_version = set()
        for i in tree.findall("//%sdependency" % POM_NS):
            for j in i:
                if j.text == "junit":
                    junit_version.add(i)

        update_junit = True
        for i in junit_version:
            print 'i', i
            for j in i:
                print j.text
                #print'test', j.text.split('.')[0]

                version = j.text.split('.')[0]
                try:
                    version = int(version)
                    if version >= 4:
                        update_junit = False
                        break
                except ValueError:
                    pass
        print update_junit
        if update_junit:
            print "DEBUG: ADDING UPDATED JUNIT"
            dependency = ElementTree.Element('%sdependency' % POM_NS)
            junit_group_id = ElementTree.SubElement(dependency, '%sgroupId' % POM_NS)
            junit_group_id.text = 'junit'
            junit_version = ElementTree.SubElement(dependency, '%sversion' % POM_NS)
            junit_version.text = '4.11'
            junit_scope = ElementTree.SubElement(dependency, '%sscope' % POM_NS)
            junit_scope.text = 'test'
            junit_artifact_id = ElementTree.SubElement(dependency, '%sartifactId' % POM_NS)
            junit_artifact_id.text = 'junit'
            for i in root.iter('%sdependencies' % POM_NS):
                i.append(dependency)

        # Add pit
        #find if build exists

        build_exists = False
        for i in tree.iter('%sbuild' % POM_NS):
            build_exists = True
            break

        plugins_exists = False
        for i in tree.iter('%splugins' % POM_NS):
            plugins_exists = True
            break

        if not plugins_exists:
            if not build_exists:
                #create build
                print "DEBUG: build and plugins do not exist, adding"
                build = ElementTree.Element('%sbuild' % POM_NS)
                ElementTree.SubElement(build, '%splugins' % POM_NS)
                for i in root.iter('%sproject' % POM_NS):
                    i.append(build)
            else:
                #build exists
                print "DEBUG: plugins do not exist, adding"
                plugins = ElementTree.Element('%splugins' % POM_NS)
                for i in root.iter('%sbuild' % POM_NS):
                    i.append(plugins)

        print "DEBUG: ADDING PIT PLUGIN"
        plugin = ElementTree.Element('%splugin' % POM_NS)
        group_id = ElementTree.SubElement(plugin, '%sgroupId' % POM_NS)
        group_id.text = 'org.pitest'
        artifact_id = ElementTree.SubElement(plugin, '%sartifactId' % POM_NS)
        artifact_id.text = 'pitest-maven'
        version = ElementTree.SubElement(plugin, '%sversion' % POM_NS)
        version.text = LATEST_PIT_VERSION
        configuration = ElementTree.SubElement(plugin, '%sconfiguration' % POM_NS)
        target_classes = ElementTree.SubElement(configuration, '%stargetClasses' % POM_NS)
        param_classes = ElementTree.SubElement(target_classes, '%sparam' % POM_NS)
        param_classes.text = mutate
        target_tests = ElementTree.SubElement(configuration, '%stargetTests' % POM_NS)
        param_tests = ElementTree.SubElement(target_tests, '%sparam' % POM_NS)
        param_tests.text = test
        for i in root.iter('%splugins' % POM_NS):
            i.append(plugin)
        tree.write(pom)
