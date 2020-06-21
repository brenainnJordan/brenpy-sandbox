'''Problem: how to organise all objects in the scene into a meaningful structure.

Created on 8 Sep 2019

@author: Bren
'''


import os
import fbx
import FbxCommon
from inspect import isclass

from brenfbx.core import bfIO

DUMP_DIR = r"D:\Repos\dataDump\brenrig"

TEST_EXPORT_FILE = os.path.join(
    DUMP_DIR,
    "fbx_property_hierarchy_example_01.fbx"
)


def create_scene(fbx_manager):
    """Create a scene with some nodes, and properties with connections/references to other nodes.
    """

    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # create some nodes
    node_1 = fbx.FbxNode.Create(fbx_manager, "node1")
    node_2 = fbx.FbxNode.Create(fbx_manager, "node2")

    object_1 = fbx.FbxObject.Create(fbx_manager, "object1")

    # add to scene
    fbx_scene.GetRootNode().AddChild(node_1)
    fbx_scene.GetRootNode().AddChild(node_2)
    fbx_scene.ConnectSrcObject(object_1)

    # create a reference property and connect nodes
    ref_prop = fbx.FbxProperty.Create(
        object_1, fbx.FbxReferenceDT, "testReferenceProperty"
    )

    ref_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    ref_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    ref_prop.ConnectSrcObject(node_1)
    ref_prop.ConnectSrcObject(node_2)

    # create hierarchal properties
    ref_dbl2_prop = fbx.FbxProperty.Create(
        object_1, fbx.FbxDouble2DT, "testReferenceDbl2Property"
    )

    ref_dbl2_prop.Set(19.0)

    ref_dbl2_prop.ConnectSrcObject(node_1)

    ref_dbl2_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    ref_dbl2_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    child_prop_1 = fbx.FbxProperty.Create(
        ref_dbl2_prop, fbx.FbxDoubleDT, "child_property1"
    )

    child_prop_1.Set(16.0)

    child_prop_1.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    child_prop_1.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    # create another sibling
    ref_dbl3_prop = fbx.FbxProperty.Create(
        object_1, fbx.FbxDouble3DT, "testReferenceDbl3Property"
    )

    ref_dbl3_prop.Set(19.0)

    # create an object connection
    object_2 = fbx.FbxObject.Create(fbx_manager, "object2")
    object_1.ConnectSrcObject(object_2)

    # create property-property connection(s)
    src_prop_1 = fbx.FbxProperty.Create(
        node_1, fbx.FbxDouble3DT, "testSrcProp1"
    )

    src_prop_1.Set(13)

    ref_prop.ConnectSrcProperty(src_prop_1)

    print "created stuff"

    # return scene
    return fbx_scene


def export_example_scene():
    """Create a manager, scene, skel and export file.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = create_scene(fbx_manager)

    if True:
        # save file using FbxCommon
        res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)
    else:
        # export file using exporter

        io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
        fbx_manager.SetIOSettings(io_settings)

        exporter = fbx.FbxExporter.Create(fbx_manager, "")

        try:
            exporter.Initialize(
                TEST_EXPORT_FILE, -1, fbx_manager.GetIOSettings()
            )
        except Exception as err:
            msg = "Call to FbxExporter::Initialize() failed.\n"
            msg += "Error returned: {0}".format(
                exporter.GetStatus().GetErrorString()
            )
            print msg
            raise err

        exporter.Export(fbx_scene)
        exporter.Destroy()

    print "file exported: {}".format(TEST_EXPORT_FILE)


def print_child_properties(fbx_property, indent):

    print " " * indent, fbx_property.GetName(), fbx_property.IsValid()

    # print children
#     child_property = fbx_property.GetFirstDescendent()
    child_property = fbx_property.GetChild()
    i = 0

    while child_property.IsValid():
        print_child_properties(child_property, indent + 1)
#         child_property = fbx_property.GetNextDescendent(child_property)
        child_property = child_property.GetSibling()
        i += 1


def get_root_properties_old(fbx_object):
    """Return a list of properties that have no parent property
    """

    root_properties = []

    fbx_property = fbx_object.GetFirstProperty()

    while fbx_property.IsValid():
        if fbx_property.GetParent().IsRoot():
            root_properties.append(fbx_property)

        fbx_property = fbx_object.GetNextProperty(fbx_property)

    return root_properties


def get_child_properties(fbx_property):
    """Return a list of child properties.
    """
    child_properties = []

    child_property = fbx_property.GetChild()

    while child_property.IsValid():
        child_properties.append(child_property)
        child_property = child_property.GetSibling()

    return child_properties


def get_root_properties(fbx_object):
    """Return a list of root-level properties.
    """
    root_properties = get_child_properties(
        fbx_object.RootProperty
    )
    return root_properties


def print_object_properties(fbx_object):

    # print object name
    object_name = fbx_object.GetName()
    print object_name, ":"

    # print root property
    for fbx_property in get_root_properties(fbx_object):
        print_child_properties(fbx_property, 1)

    print "\n"


def inspect_properties(file_path):

    fbx_scene, fbx_manager = bfIO.load_fbx_file(
        file_path,
        fbx_manager=None,
        settings=None,
        verbose=True,
        err=True
    )

    src_count = fbx_scene.GetSrcObjectCount()

    # print properties
    for i in range(src_count):
        src = fbx_scene.GetSrcObject(i)
        print_object_properties(src)

    # cleanup
    fbx_manager.Destroy()
    del fbx_manager, fbx_scene

    print "done"


if __name__ == "__main__":
    export_example_scene()
    inspect_properties(TEST_EXPORT_FILE)
#     inspect_example_scene()
    print "done"
