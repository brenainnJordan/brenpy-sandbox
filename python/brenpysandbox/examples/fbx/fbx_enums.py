'''
Created on 9 Mar 2019

@author: Bren

notes:

Fbx python Enums are a little weird, hard to explain, and don't seem to work the same as cpp enums.


# cpp enums
https://www.learncpp.com/cpp-tutorial/4-5a-enum-classes/

The concept of cpp enums do not translate well to python, 
Python fbx enums are wrapped by sip,
first as a class representing the enum subclassed from sip.enumtype.

Secondly the enum values are created as class members,
pointing to instances of the class with a value unique accross
instances of that class.

See below sudo code examples of enums created in this structure.


# inherited enums

Inheritance results in subclasses holding many non-applicable enums. 

eg.
FbxSkeleton inherits a lot of enums from FbxNodeAttribute:

eBoundary
eCachedEffect
eCamera
eCameraStereo
eCameraSwitcher
eContentLoaded
eDeepClone
eDontLocalize
eEffector
eHidden
eInitialized
eLODGroup
eLight
eLimb
eLimbNode
eLine
eMarker
eMesh
eNone
eNull
eNurbs
eNurbsCurve
eNurbsSurface
eOpticalMarker
eOpticalReference
ePatch
eReferenceClone
eRoot
eSavable
eSelected
eShape
eSkeleton
eSubDiv
eSystem
eTrimNurbsSurface
eUnknown

but only uses these:
    eEffector 3 <class 'fbx.EType'> <class 'fbx.EType'>
    eLimb 1 <class 'fbx.EType'> <class 'fbx.EType'>
    eLimbNode 2 <class 'fbx.EType'> <class 'fbx.EType'>
    eRoot 0 <class 'fbx.EType'> <class 'fbx.EType'>

cpp Enums are well documented under the "EType" documentation for each cpp class.

http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_cpp_ref_class_fbx_skeleton_html

# enum names/labels

# enum classes

EFbxQuatInterpMode
EFbxRotationOrder
EFbxType

'''

import fbx


class EnumTestTypeA(object):
    """sip.enumtype class looks something like this"""

    def __init__(self, i):
        self.i = i

    def __rep__(self):
        return str(self.i)

    def __str__(self):
        return str(self.i)


class EnumTestTypeB(object):
    """sip.enumtype class looks something like this"""

    def __init__(self, i):
        self.i = i

    def __rep__(self):
        return str(self.i)

    def __str__(self):
        return str(self.i)

    def __eq__(self, other):
        return self.i == other.i


class Thing(object):
    """sip.enumtype subclasses are instanced as enums something like this.
    """
    eTestA1 = EnumTestTypeA(1)
    eTestA2 = EnumTestTypeA(2)

    eTestB1 = EnumTestTypeB(1)
    eTestB2 = EnumTestTypeB(2)


def sudo_enum_test():
    print "Sudo enum test..."
    print "\t", Thing.eTestB1  # 1
    print "\t", Thing.eTestA1 == Thing.eTestB1  # True


def print_enum_type_test():
    """Testing the behaviour of fbx enums"""

    # in cpp, enums can be defined as enum or enum class
    # enum classes are typed, meaning if an enum type shares the same int
    # they cannot be compared as equal

    # however in python fbx this is not the case
    print "typed test..."
    print "\t", fbx.FbxSkeleton.eRoot == fbx.FbxSkeleton.eDeepClone  # True
    print "\t", fbx.eEulerXYZ == fbx.FbxSkeleton.eDeepClone  # True
    # however you can compare the python type to differentiate enums
    # with the same value
    print "\t", type(
        fbx.eEulerXYZ
    ) == type(
        fbx.FbxSkeleton.eDeepClone
    )  # False
    print "\n"


def print_fbx_eums():
    """Get all fbx enum names and their ints.

    Note how some ints repeat
    this suggests that in cpp several enums were defined
    and during the python wrapping they were all bundled together
    (with class for each enum type)
    """
    print "fbx enums"
    for i in dir(fbx):
        if i.startswith("e"):
            cls = getattr(fbx, i)
            print "\t", i, cls, type(cls)
    print "\n"
    print "\tfbx.eEulerXZY == fbx.eFbxChar: ", fbx.eEulerXZY == fbx.eFbxChar  # True
    print "\n"


def print_fbx_skeleton_enums():
    print "FbxSkeleton enums"
    for i in dir(fbx.FbxSkeleton):
        if i.startswith("e"):
            cls = getattr(fbx.FbxSkeleton, i)
            print "\t", i, cls, type(cls)
    print "\n"

    print "FbxSkeleton filtered enums"
    for i in dir(fbx.FbxSkeleton):
        if i.startswith("e"):
            cls = getattr(fbx.FbxSkeleton, i)
            if type(cls) == fbx.FbxSkeleton.EType:
                print "\t", i, cls, type(cls)
    print "\n"


def print_fbx_enum_classes():
    print "fbx enum classes:"

    for i in dir(fbx):
        cls = getattr(fbx, i)

        if cls.__class__.__name__ == "enumtype":
            print "\t", i

    print "\n"

    print "fbx.FbxSkeleton enum classes:"

    for i in dir(fbx.FbxSkeleton):
        try:
            cls = getattr(fbx.FbxSkeleton, i)

            if cls.__class__.__name__ == "enumtype":
                print "\t", i
        except AttributeError:
            pass

    print "\n"


def print_enum_base_class():
    print "Enum base class:"
    print "\tfbx.EFbxType: ", type(fbx.EFbxType)  # <type 'sip.enumtype'>
    print "\tfbx.eFbxChar is instance of fbx.EFbxType: ", isinstance(
        fbx.eFbxChar, fbx.EFbxType)  # True
    print "\n"


def print_enum_help():
    print "Enum help..."
    for i in dir(fbx.FbxSkeleton.EType):
        print "\t", i

    print "\n"
    print help(fbx.FbxSkeleton.EType)
    print "\t", fbx.FbxSkeleton.EType.__dict__
    print "\t", fbx.FbxSkeleton.eRoot.__reduce__()
    print "\n"


def print_enum_usage_test():
    """Use an enum in the context of FbxNodeAttribute/FbxSkeleton.

    When passing a fbx enum into a fbx method call,
    checks are made that the enum class matches that of the parent enum class.

    """

    fbx_manager = fbx.FbxManager.Create()
    skel_attr = fbx.FbxSkeleton.Create(fbx_manager, "skel_test_attribute")

    print "enum value plus type test..."
    print "\t",  fbx.FbxSkeleton.eCamera
    print "\t", fbx.eEulerXYZ
    print "\t",  fbx.FbxSkeleton.eDeepClone
    print "\t", fbx.FbxSkeleton.eRoot

    try:
        # first try using an fbx enum with the same int value (0)
        skel_attr.SetSkeletonType(fbx.eEulerXYZ)
        # TypeError: SetSkeletonType(self, FbxSkeleton.EType):
        # argument 1 has unexpected type 'EFbxRotationOrder'

    except TypeError:
        try:
            # next try using an enum inherited from FbxNodeAttribute
            skel_attr.SetSkeletonType(fbx.FbxSkeleton.eCamera)
            # TypeError: SetSkeletonType(self, FbxSkeleton.EType):
            # argument 1 has unexpected type 'EType'
            # (referring to FbxNodeAttribute.EType)

        except TypeError:
            try:
                # next try using an inherited enum with the same int value (0)
                skel_attr.SetSkeletonType(fbx.FbxSkeleton.eDeepClone)
                # TypeError: SetSkeletonType(self, FbxSkeleton.EType):
                # argument 1 has unexpected type 'ECloneType'
                # (refering to FbxObject.ECloneType)

            except TypeError:
                # accepts expected enum type FbxSkeleton.EType
                skel_attr.SetSkeletonType(fbx.FbxSkeleton.eRoot)


if __name__ == "__main__":

    sudo_enum_test()
    print_enum_type_test()
    print_fbx_eums()
    print_fbx_skeleton_enums()
    print_fbx_enum_classes()
    print_enum_base_class()
    print_enum_help()
    print_enum_usage_test()
