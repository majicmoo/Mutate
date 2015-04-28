__author__ = 'Megan'

import xml.etree.ElementTree as ElementTree

POM_NS = "{http://maven.apache.org/POM/4.0.0}"
LATEST_PIT_VERSION = "1.1.2"
LATEST_JAVALANCHE_VERSION = "1.7"
LATEST_JUDY_VERSION = "1.7"

ElementTree.register_namespace("", "http://maven.apache.org/POM/4.0.0")
import os


class ConvertXML(object):

    @staticmethod
    def convert_pom(mutate, test, pom):
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
                # print 'test', j.text.split('.')[0]
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
        # Find if build exists
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
                # Create build
                print "DEBUG: build and plugins do not exist, adding"
                build = ElementTree.Element('%sbuild' % POM_NS)
                ElementTree.SubElement(build, '%splugins' % POM_NS)
                for i in root.iter('%sproject' % POM_NS):
                    i.append(build)
            else:
                # Build exists
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

    @staticmethod
    def convert_pom_javalanche(mutate, test, pom):
        path_target = test.split(os.sep)
        path_target = test[:-len(path_target[len(path_target)-1])]

        tree = ElementTree.parse(pom)
        root = tree.getroot()

        # # Update Junit
        # junit_version = set()
        # for i in tree.findall("//%sdependency" % POM_NS):
        #     for j in i:
        #         if j.text == "junit":
        #             junit_version.add(i)
        #
        # update_junit = True
        # for i in junit_version:
        #     print 'i', i
        #     for j in i:
        #         print j.text
        #         # print 'test', j.text.split('.')[0]
        #         version = j.text.split('.')[0]
        #         try:
        #             version = int(version)
        #             if version >= 4:
        #                 update_junit = False
        #                 break
        #         except ValueError:
        #             pass
        # print update_junit
        # if update_junit:
        #     print "DEBUG: ADDING UPDATED JUNIT"
        #     dependency = ElementTree.Element('%sdependency' % POM_NS)
        #     junit_group_id = ElementTree.SubElement(dependency, '%sgroupId' % POM_NS)
        #     junit_group_id.text = 'junit'
        #     junit_version = ElementTree.SubElement(dependency, '%sversion' % POM_NS)
        #     junit_version.text = '4.11'
        #     junit_scope = ElementTree.SubElement(dependency, '%sscope' % POM_NS)
        #     junit_scope.text = 'test'
        #     junit_artifact_id = ElementTree.SubElement(dependency, '%sartifactId' % POM_NS)
        #     junit_artifact_id.text = 'junit'
        #     for i in root.iter('%sdependencies' % POM_NS):
        #         i.append(dependency)

        # Add javalanche
        # Find if build exists
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
                # Create build
                print "DEBUG: build and plugins do not exist, adding"
                build = ElementTree.Element('%sbuild' % POM_NS)
                ElementTree.SubElement(build, '%splugins' % POM_NS)
                for i in root.iter('%sproject' % POM_NS):
                    i.append(build)
            else:
                # Build exists
                print "DEBUG: plugins do not exist, adding"
                plugins = ElementTree.Element('%splugins' % POM_NS)
                for i in root.iter('%sbuild' % POM_NS):
                    i.append(plugins)

        print "DEBUG: ADDING JAVALANCHE PLUGIN"
        plugin = ElementTree.Element('%splugin' % POM_NS)
        group_id = ElementTree.SubElement(plugin, '%sgroupId' % POM_NS)
        group_id.text = 'org.apache.maven.plugins'
        artifact_id = ElementTree.SubElement(plugin, '%sartifactId' % POM_NS)
        artifact_id.text = 'maven-antrun-plugin'
        version = ElementTree.SubElement(plugin, '%sversion' % POM_NS)
        version.text = LATEST_JAVALANCHE_VERSION
        configuration = ElementTree.SubElement(plugin, '%sconfiguration' % POM_NS)
        target = ElementTree.SubElement(configuration, '%starget' % POM_NS)
        ant = ElementTree.SubElement(target,  '%sant' % POM_NS)
        ant.set('dir','javalanche')
        ant.set('antfile','javalanche.xml')
        ant.set('target', 'mutationTest')
        property_one = ElementTree.SubElement(ant, '%sproperty' % POM_NS)
        property_one.set('name','prefix')
        property_one.set('value', path_target)
        property_two = ElementTree.SubElement(ant, '%sproperty' % POM_NS)
        property_two.set('name','cp')
        property_two.set('value', '../target/classes:../target/test-classes')
        property_three = ElementTree.SubElement(ant, '%sproperty' % POM_NS)
        property_three.set('name','tests')
        property_three.set('value', test)
        property_four = ElementTree.SubElement(ant, '%sproperty' % POM_NS)
        property_four.set('name','javalanche')
        property_four.set('value', ".")

        for i in root.iter('%splugins' % POM_NS):
            i.append(plugin)
        tree.write(pom)

    @staticmethod
    def convert_pom_judy(mutate, test, pom):
        path_target = test.split(os.sep)
        path_target = test[:-len(path_target[len(path_target)-1])]

        tree = ElementTree.parse(pom)
        root = tree.getroot()

        # # Update Junit
        # junit_version = set()
        # for i in tree.findall("//%sdependency" % POM_NS):
        #     for j in i:
        #         if j.text == "junit":
        #             junit_version.add(i)
        #
        # update_junit = True
        # for i in junit_version:
        #     print 'i', i
        #     for j in i:
        #         print j.text
        #         # print 'test', j.text.split('.')[0]
        #         version = j.text.split('.')[0]
        #         try:
        #             version = int(version)
        #             if version >= 4:
        #                 update_junit = False
        #                 break
        #         except ValueError:
        #             pass
        # print update_junit
        # if update_junit:
        #     print "DEBUG: ADDING UPDATED JUNIT"
        #     dependency = ElementTree.Element('%sdependency' % POM_NS)
        #     junit_group_id = ElementTree.SubElement(dependency, '%sgroupId' % POM_NS)
        #     junit_group_id.text = 'junit'
        #     junit_version = ElementTree.SubElement(dependency, '%sversion' % POM_NS)
        #     junit_version.text = '4.11'
        #     junit_scope = ElementTree.SubElement(dependency, '%sscope' % POM_NS)
        #     junit_scope.text = 'test'
        #     junit_artifact_id = ElementTree.SubElement(dependency, '%sartifactId' % POM_NS)
        #     junit_artifact_id.text = 'junit'
        #     for i in root.iter('%sdependencies' % POM_NS):
        #         i.append(dependency)

        # Add javalanche
        # Find if build exists
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
                # Create build
                print "DEBUG: build and plugins do not exist, adding"
                build = ElementTree.Element('%sbuild' % POM_NS)
                ElementTree.SubElement(build, '%splugins' % POM_NS)
                for i in root.iter('%sproject' % POM_NS):
                    i.append(build)
            else:
                # Build exists
                print "DEBUG: plugins do not exist, adding"
                plugins = ElementTree.Element('%splugins' % POM_NS)
                for i in root.iter('%sbuild' % POM_NS):
                    i.append(plugins)

        print "DEBUG: ADDING JAVALANCHE PLUGIN"
        plugin = ElementTree.Element('%splugin' % POM_NS)
        group_id = ElementTree.SubElement(plugin, '%sgroupId' % POM_NS)
        group_id.text = 'org.apache.maven.plugins'
        artifact_id = ElementTree.SubElement(plugin, '%sartifactId' % POM_NS)
        artifact_id.text = 'maven-antrun-plugin'
        version = ElementTree.SubElement(plugin, '%sversion' % POM_NS)
        version.text = LATEST_JUDY_VERSION
        configuration = ElementTree.SubElement(plugin, '%sconfiguration' % POM_NS)
        target = ElementTree.SubElement(configuration, '%starget' % POM_NS)

        java = ElementTree.SubElement(target, '%sjava' % POM_NS)
        java.set('dir','judy')
        java.set('jar','judy/judy-2.1.0.jar')
        java.set('fork','true')

        jvmarg1 = ElementTree.SubElement(java,'%sjvmarg' % POM_NS)
        jvmarg1.set('value', 'XX:MaxPermSize=2048m')
        jvmarg2 = ElementTree.SubElement(java,'%sjvmarg' % POM_NS)
        jvmarg2.set('value', '-Xmx2048m')
        jvmarg3 = ElementTree.SubElement(java,'%sjvmarg' % POM_NS)
        jvmarg3.set('value', '-Xms2048m')
        jvmarg4 = ElementTree.SubElement(java,'%sjvmarg' % POM_NS)
        jvmarg4.set('value', '-Xmn512m')
        jvmarg5 = ElementTree.SubElement(java,'%sjvmarg' % POM_NS)
        jvmarg5.set('value', 'Xss512k')
        jvmarg6 = ElementTree.SubElement(java,'%sjvmarg' % POM_NS)
        jvmarg6.set('value', '-XX:+UseG1GC')
        arg1 = ElementTree.SubElement(java,'%sarg' % POM_NS)
        arg1.set('value','-w ${project.build.directory}')
        arg2 = ElementTree.SubElement(java,'%sarg' % POM_NS)
        arg2.set('value','-c classes')
        arg3 = ElementTree.SubElement(java,'%sarg' % POM_NS)
        arg3.set('value','-t test-classes')
        for i in root.iter('%splugins' % POM_NS):
            i.append(plugin)
        tree.write(pom)