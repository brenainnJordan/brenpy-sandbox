'''
Created on Apr 16, 2017

@author: User
'''

class blah(object):
    '''
    classdocs
    '''


    def __init__(self, derp=10):
        '''
        Constructor
        '''
        self.thing = 24*2
        self.stuff = 'blah'
        self.flerp = derp*3
        self.derp = derp
    
    def print_things(self):
        print self.thing
        print self.stuff
        print self.derp
        print self.flerp
        


class thing(blah):
    
    def __init__(self):
        #blah.__init__(self)
        super(thing, self).__init__(derp=20)
        self.blorp = True
    
    def print_blah(self):
        print self.blorp


if __name__ in ['__main__', '__builtin__']:
    i = thing()
    i.print_blah()
    i.print_things()
    print i.thing