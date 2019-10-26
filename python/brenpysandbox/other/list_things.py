'''
Created on Jul 24, 2017

@author: User
'''


test = range(1000)

#blah = test[2:4::10]

#print blah


from itertools import islice

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

print list(chunk(range(100000), 3))