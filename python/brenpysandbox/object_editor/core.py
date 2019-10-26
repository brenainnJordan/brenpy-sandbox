'''
Created on 13 May 2018

@author: Bren
'''

class ObjectList(object):
    pass

class Object(object):
    def __init__(self):
        #self._components = ComponentList()
        self._name = None
    
    def name(self):
        return self._name
    
    def setName(self, name):
        self._name = str(name) 
