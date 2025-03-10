"""Testing python objects
"""

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

    def __set__(self, obj, value):
        raise
        super(ClassProperty, self).__set__(type(obj), value)

    def __delete__(self, obj):
        raise
        super(ClassProperty, self).__delete__(type(obj))


class TestThing(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

    def __set__(self, owner_self, owner_cls):
        raise
        return self.fget(owner_cls)

