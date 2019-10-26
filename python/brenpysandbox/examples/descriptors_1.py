'''
Created on 18 Jul 2019

@author: Bren


https://python-reference.readthedocs.io/en/latest/docs/dunderdsc/get.html

'''

# example 1 ---

# this is our descriptor object


class Bar(object):
    def __init__(self):
        self.value = ''

    def __get__(self, instance, owner):
        print "returned from descriptor object"
        return self.value

    def __set__(self, instance, value):
        print "set in descriptor object"
        self.value = value

    def __delete__(self, instance):
        print "deleted in descriptor object"
        del self.value


class Foo(object):
    bar = Bar()


def descriptor_test_1():

    print "instancing Foo..."
    f = Foo()

    # __set__
    print "\nsetting bar..."
    f.bar = 10
    # set in descriptor object

    # __get__
    print "\nprinting bar..."
    print f.bar
    # returned from descriptor object
    # 10

    # __delete__
    print "\ndeleting bar..."
    del f.bar
    # deleted in descriptor object


# example 2 ---

class Bar2(object):
    def __init__(self):
        self.value = 'test'

    def __get__(self, instance, owner):
        print instance, owner
        return self.value

    def __set__(self, instance, value):
        print instance, value
        self.value = value

    def __delete__(self, instance):
        print instance
        del self.value


class Foo2(object):
    bar = Bar2()


def descriptor_test_2():

    print "instancing Foo2..."
    f = Foo2()

    # __get__
    print "\ngetting bar..."
    print f.bar
    # <__main__.Foo2 object at 0x00000000038E9710> <class '__main__.Foo2'>
    # test

    # __set__
    print "\nsetting bar..."
    f.bar = 10
    # <__main__.Foo2 object at 0x0000000002CA9710> 10

    # __delete__
    print "\ndeleting bar..."
    del f.bar
    # <__main__.Foo2 object at 0x0000000002CA9710>


# example 3 ---

class Bar3(object):

    name = "Bar3_name"

    def __init__(self):
        pass

    @classmethod
    def Foo(cls, value):
        print "{} {} {}".format(cls.name, value, cls)

#     @classmethod
#     def Foo(*args):
#         print args


class BarChild(Bar3):
    """
    https://blogs.gnome.org/jamesh/2005/06/23/overriding-class-methods-in-python/
    """

    name = "BarChild_name"
    use_super = False

    def __init__(self):
        Bar3.__init__(self)

    @classmethod
    def Foo(cls, value):
        if cls.use_super:
            super(BarChild, cls).Foo(value)
        else:
            if False:
                Bar3.Foo(cls, value)  # errors (too many args)

            elif False:
                foo_method = getattr(Bar3, "Foo")
                print foo_method
                foo_method(cls, value)  # also errors

            elif False:
                # doesn't error but doesn't use BarChild as expected
                print "__get__ {}".format(cls)
                Bar3.Foo.__get__(cls)(value)
            else:
                # this works!
                print "__func__"
                Bar3.Foo.__func__(cls, value)

#                 Bar3.Foo.im_func(cls, value) # also works

        print "BarChild {}".format(value)


def descriptor_test_3():
    #     bar = Bar3()
    Bar3.Foo("test")

#     child = BarChild()
    BarChild.Foo("test")


if __name__ == "__main__":
    #     descriptor_test_1()
    #     descriptor_test_2()
    descriptor_test_3()
