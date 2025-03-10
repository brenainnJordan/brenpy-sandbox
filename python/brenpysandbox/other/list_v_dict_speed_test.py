import time

def test_int_key_1():
    count = 100000
    list_test = [(i, "test_{}".format(i)) for i in range(count)]
    dict_test = {i: "test_{}".format(i) for i in range(count)}

    div = 100

    for i in range(div+1):
        test_index = ((count-1)/div) * i

        print "test index", test_index

        list_start_time = time.time()

        for a, b in list_test:
            if a == test_index:
                break

        list_end_time = time.time()

        print "list time: {:10f}".format(list_end_time - list_start_time)

        dict_start_time = time.time()

        a = dict_test[test_index]

        dict_end_time = time.time()

        print "dict time: {:10f}".format(dict_end_time - dict_start_time)

def test_str_key_1():
    count = 100000
    list_test = [(str(i), "test_{}".format(i)) for i in range(count)]
    dict_test = {str(i): "test_{}".format(i) for i in range(count)}

    div = 100

    for i in range(div+1):
        test_index = str(((count-1)/div) * i)

        print "test index", test_index

        list_start_time = time.time()

        for a, b in list_test:
            if a == test_index:
                break

        list_end_time = time.time()

        print "list time: {:10f}".format(list_end_time - list_start_time)

        dict_start_time = time.time()

        a = dict_test[test_index]

        dict_end_time = time.time()

        print "dict time: {:10f}".format(dict_end_time - dict_start_time)


def test_int_key_2():
    count = 100000
    list_test = [(i, "test_{}".format(i)) for i in range(count)]
    dict_test = {i: "test_{}".format(i) for i in range(count)}

    div = 100

    list_start_time = time.time()

    for i in range(div+1):
        test_index = ((count-1)/div) * i

        for a, b in list_test:
            if a == test_index:
                break

    list_end_time = time.time()
    print "list time: {:10f}".format(list_end_time - list_start_time)

    dict_start_time = time.time()

    for i in range(div+1):
        test_index = ((count-1)/div) * i
        a = dict_test[test_index]

    dict_end_time = time.time()
    print "dict time: {:10f}".format(dict_end_time - dict_start_time)


def test_str_key_2():
    count = 100000
    list_test = [(str(i), "test_{}".format(i)) for i in range(count)]
    dict_test = {str(i): "test_{}".format(i) for i in range(count)}

    div = 100

    list_start_time = time.time()

    for i in range(div+1):
        test_index = str(((count-1)/div) * i)

        for a, b in list_test:
            if a == test_index:
                break

    list_end_time = time.time()
    print "list time: {:10f}".format(list_end_time - list_start_time)

    dict_start_time = time.time()

    for i in range(div+1):
        test_index = str(((count-1)/div) * i)
        a = dict_test[test_index]

    dict_end_time = time.time()
    print "dict time: {:10f}".format(dict_end_time - dict_start_time)


# test_int_key_1()
# test_str_key_1()
# test_int_key_2()
test_str_key_2()
