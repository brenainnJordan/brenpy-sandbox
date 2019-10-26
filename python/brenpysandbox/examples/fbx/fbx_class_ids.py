"""FbxClassclass_id examples and usage.

Notes:
    FbxMangager must first be created for FbxClassclass_id objects to be valclass_id.
    Who knew?!

"""

import inspect
import fbx


def print_fbx_object_type_class_ids():
    """
    """
    fbx_manager = fbx.FbxManager.Create()

    for i in dir(fbx):
        cls = getattr(fbx, i)
        if not inspect.isclass(cls):
            continue

        if issubclass(cls, fbx.FbxObject):
            class_id = cls.ClassId

            print class_id.GetName()
            print "\tParent: ", class_id.GetParent().GetName()
            print "\tFbxFileTypeName", class_id.GetFbxFileTypeName()
            print "\tFbxFileSubTypeName", class_id.GetFbxFileSubTypeName()


if __name__ == "__main__":
    print_fbx_object_type_class_ids()
