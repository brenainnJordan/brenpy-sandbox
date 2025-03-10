import time

class TestA(object):
    def __init__(self):
        pass

class TestB(object):
    def __init__(self):
        pass

class TestC(object):
    def __init__(self):
        pass


test_int_dict = {
    i: "test{}".format(i) for i in range(1000)
}

test_str_dict = {
    str(i): "test{}".format(i) for i in range(1000)
}

test_long_str_dict = {
    "{0:010d}".format(i): "test{}".format(i) for i in range(1000)
}

test_class_dict = {
    i: "test{}".format(i) for i in [TestA, TestB, TestC]
}


test_list = []
start = time.time()

for i in range(1000):
    test = test_int_dict[i]
    test_list.append(test)

print "int look up: {}ms".format((time.time() - start) * 1000)



str_keys = [str(i) for i in range(1000)]
test_list = []
start = time.time()

for i in str_keys:
    test = test_str_dict[i]
    test_list.append(test)

print "str int look up: {}ms".format((time.time() - start) * 1000)



test_list = []
start = time.time()

for i in range(1000):
    test = test_class_dict[TestA]
    test_list.append(test)

print "class look up: {}ms".format((time.time() - start) * 1000)


str_keys = ["{0:010d}".format(i) for i in range(1000)]
test_list = []
start = time.time()

for i in str_keys:
    test = test_long_str_dict[i]
    test_list.append(test)

print "long str int look up: {}ms".format((time.time() - start) * 1000)
