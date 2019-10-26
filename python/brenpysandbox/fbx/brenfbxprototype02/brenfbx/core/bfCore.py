'''
Created on 1 Sep 2019

@author: Bren
'''


class BFbxError(Exception):
    def __init__(self, *args):
        super(BFbxError, self).__init__(*args)
