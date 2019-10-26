'''
Created on 4 Jun 2018

@author: Bren
'''

class Data(object):
    TYPE = None
    
    def __init__(self, name):
        self._name = None
        self._value = None
        
        self.setName(name)
    
    def name(self):
        return self._name
    
    def setName(self, name):
        self._name = str(name)
    
    def value(self):
        return self._value
    
    def setValuue(self, value):
        self._value = self.TYPE(value)
    

class Integer(Data):
    TYPE = int
    
    def __init__(self, name):
        super(Integer, self).__init__(name)


if __name__ == "__main__":
    test = Integer("test")
    test.setValuue("seg")
    print test.value()