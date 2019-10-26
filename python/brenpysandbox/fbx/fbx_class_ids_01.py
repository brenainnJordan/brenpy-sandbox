'''
Created on 8 Sep 2019

@author: Bren
'''

import fbx
from inspect import isclass


def test1():
    for i in dir(fbx):
        obj = getattr(fbx, i)

        if not isclass(obj):
            continue

        if not issubclass(obj, fbx.FbxObject):
            continue

        print obj


if __name__ == "__main__":
    test1()
