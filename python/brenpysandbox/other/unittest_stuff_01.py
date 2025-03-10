import unittest
import inspect

test_path = r"D:\Repos\brenpy\tests\brenpytests\unittests\items"


loader = unittest.TestLoader()

test_suite = loader.discover(test_path)

print "test_suite", test_suite

for test_suite_i in test_suite:
    # print test_suite_i.__doc__
    # print dir(test_suite_i)
    # print test_suite_i._get_previous_module()

    # '__call__', '__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__iter__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_addClassOrModuleLevelException', '_get_previous_module', '_handleClassSetUp', '_handleModuleFixture', '_handleModuleTearDown', '_tearDownPreviousClass', '_tests', 'addTest', 'addTests', 'countTestCases', 'debug', 'run']

    # print type(test_suite_i)

    for test_suite_j in test_suite_i:
        print "\t", test_suite_j
        for test_case in test_suite_j:
            # print "\t\t type", type(test_case)
            print "\t\t test case file", inspect.getfile(test_case.__class__)
            print "\t\t test case module", test_case.__module__ # (str)
            # print "\t\t test case module type", type(test_case.__module__) # (str)
            # print "\t\t test case module dir", dir(test_case.__module__)
            print "\t\t test case name", test_case.__class__.__name__
            print "\t\t test case (selected) method", test_case._testMethodName
            print "\t\t test case docs", test_case._testMethodDoc
            print "\t\t dir", dir(test_case)
