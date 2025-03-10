# Define a class with slots for name and age
class Person(object):
    __slots__ = 'name', 'age'

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f'Person(name={self.name}, age={self.age})'

if __name__ == "__main__":
    # Create an instance of the class
    p = Person('Alice', 25)
    print(p) # Person(name=Alice, age=25)

    # Try to add a new attribute
    p.gender = 'female' # AttributeError: 'Person' object has no attribute 'gender'
