class First(object):
    def __init__(self):
        super(First, self).__init__()
        print("first")

class Second(object):
    def __init__(self):
        super(Second, self).__init__()
        print("second")

class Third(First, Second):
    def __init__(self):
        super(Third, self).__init__()
        print("third")


class FirstParam(object):
    def __init__(self, param1):
        super(FirstParam, self).__init__()
        print("first", param1)

class SecondParam(object):
    def __init__(self, param1):
        super(SecondParam, self).__init__()
        print("second", param1)

class ThirdParam(FirstParam, Second):
    def __init__(self, param1):
        super(ThirdParam, self).__init__(param1)
        print("third", param1)


# class First(object):
#     def __init__(self):
#         super(First, self).__init__()
#         print("first")

class SecondDerived(Second):
    def __init__(self):
        super(SecondDerived, self).__init__()
        print("second derived")

class ThirdDerived(SecondDerived, First):
    def __init__(self):
        super(ThirdDerived, self).__init__()
        print("third derived")

if __name__ == "__main__":
    # test = Third()
    # test1 = ThirdParam("test")
    test2 = ThirdDerived()