'''Problem: how to organise all objects in the scene into a meaningful structure.

Created on 8 Sep 2019

@author: Bren
'''

'''
Created on 7 Sep 2019

@author: Bren
'''
import os
import fbx
import FbxCommon
from inspect import isclass

DUMP_DIR = r"D:\Repos\dataDump\brenrig"

TEST_EXPORT_FILE = os.path.join(
    DUMP_DIR,
    "fbx_scene_sorting_example_01.fbx"
)


def create_example_scene(fbx_manager):
    """Create a scene containing some example node and object connections
    """
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "test_scene")

    # create some nodes under the root node
    root_child_1 = fbx.FbxNode.Create(fbx_manager, "root_child_1")
    root_child_2 = fbx.FbxNode.Create(fbx_manager, "root_child_2")
    root_child_3 = fbx.FbxNode.Create(fbx_manager, "root_child_3")
    root_child_4 = fbx.FbxNode.Create(fbx_manager, "root_child_4")

    fbx_scene.GetRootNode().AddChild(root_child_1)
    fbx_scene.GetRootNode().AddChild(root_child_2)

    root_child_2.AddChild(root_child_3)
    root_child_3.AddChild(root_child_4)

    # create some nodes connected to the scene
    # but not under root
    node_1 = fbx.FbxNode.Create(fbx_manager, "node_1")
    node_2 = fbx.FbxNode.Create(fbx_manager, "node_2")
    node_3 = fbx.FbxNode.Create(fbx_manager, "node_3")
    node_4 = fbx.FbxNode.Create(fbx_manager, "node_4")
    node_5 = fbx.FbxNode.Create(fbx_manager, "node_5")

    # connect top nodes to the scene using connections
    fbx_scene.ConnectSrcObject(node_1)
    fbx_scene.ConnectSrcObject(node_2)

    # (always) add children as normal
    node_2.AddChild(node_3)
    node_3.AddChild(node_4)
    node_1.AddChild(node_5)

    # create some objects
    object_1 = fbx.FbxObject.Create(fbx_manager, "object_1")
    object_2 = fbx.FbxObject.Create(fbx_manager, "object_2")
    object_3 = fbx.FbxObject.Create(fbx_manager, "object_3")

    print "instanced object class id: ", object_1.GetClassId().GetName()
    print fbx.FbxObject.ClassId == object_1.GetClassId()
    print fbx.FbxObject.ClassId != node_1.GetClassId()

    # object should have no hierarchy
    fbx_scene.ConnectSrcObject(object_1)
    fbx_scene.ConnectSrcObject(object_2)
    fbx_scene.ConnectSrcObject(object_3)

    # meta data test
#     meta_1 = fbx.FbxObjectMetaData.Create(fbx_manager, "meta_1")
#     fbx.FbxEnvironment

    # collection exclusive objects do save with the scene
    collection_exclusive_1 = fbx.FbxCollectionExclusive.Create(
        fbx_manager, "test_collection_exclusive_1"
    )

    fbx_scene.ConnectSrcObject(collection_exclusive_1)
    collection_exclusive_1.AddMember(object_2)

    # layers (inherits from collectionExclusive) also do save with scene
    layer_1 = fbx.FbxDisplayLayer.Create(fbx_manager, "test_layer")
    fbx_scene.ConnectSrcObject(layer_1)
    layer_1.AddMember(object_1)
    layer_1.AddMember(node_1)

    # selection set, non-exclusive, inherits from FbxCollection, but DOES save
    # with scene!
    set_1 = fbx.FbxSelectionSet.Create(fbx_manager, "test_selection_set_1")
    fbx_scene.ConnectSrcObject(set_1)
    set_1.AddMember(object_1)
    set_1.AddMember(node_1)

    set_2 = fbx.FbxSelectionSet.Create(fbx_manager, "test_selection_set_2")
    fbx_scene.ConnectSrcObject(set_2)
    set_2.AddMember(object_1)
    set_2.AddMember(node_1)

    # return scene
    return fbx_scene


def export_example_scene():
    """Create a manager, scene, skel and export file.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = create_example_scene(fbx_manager)

    print "Pre-save Destinations:"
    print print_destinations(fbx_scene, 1)

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


def print_children(node, indent, debug=True):
    for i in range(node.GetChildCount()):
        child_node = node.GetChild(i)

        msg = "  " * indent
        msg += child_node.GetName()

        if debug:
            msg += " (child of {})".format(node.GetName())

        print msg

        print_children(child_node, indent + 1, debug=debug)


def print_connected(fbx_object, indent, recursive=True, include_children=True, debug=True):
    for i in range(fbx_object.GetSrcObjectCount()):
        src_object = fbx_object.GetSrcObject(i)

        msg = "  " * indent
        msg += src_object.GetName()

        if debug:
            msg += " (-> {})".format(fbx_object.GetName())

        print msg

        if isinstance(src_object, fbx.FbxNode) and include_children:
            print_children(src_object, indent + 1, debug=debug)

        if recursive:
            print_connected(
                src_object, indent + 1, recursive=True, include_children=True, debug=debug
            )


def print_primary_connected(fbx_object, indent, recursive=True, debug=True):

    # find source objects where this object is the first destination
    primary_connected = []

    for i in range(fbx_object.GetSrcObjectCount()):
        src_object = fbx_object.GetSrcObject(i)

        if src_object.GetDstObject(0) == fbx_object:
            primary_connected.append(src_object)

    for src_object in primary_connected:
        msg = "  " * indent
        msg += src_object.GetName()

        if debug:
            msg += " (-> {})".format(fbx_object.GetName())

        print msg

        if recursive:
            print_connected(
                src_object, indent + 1, recursive=True, include_children=True, debug=debug
            )


def print_destinations(fbx_scene, indent):
    for i in range(fbx_scene.GetSrcObjectCount()):
        src_object = fbx_scene.GetSrcObject(i)

        msg = "  " * indent
        msg += src_object.GetName()
        print msg

        for j in range(src_object.GetDstObjectCount()):
            dst_object = src_object.GetDstObject(j)

            msg = "  " * (indent + 1)
            msg += dst_object.GetName()
            print msg


def print_organised_children(fbx_scene):
    for i in range(fbx_scene.GetSrcObjectCount()):
        src_object = fbx_scene.GetSrcObject(i)

        # ignore anything that isn't a node
        if not isinstance(src_object, fbx.FbxNode):
            continue

        # we are only interested in top level nodes
        if src_object.GetParent() is not None:
            continue

        # print hierarchy
        print "  ", src_object.GetName()
        print_children(src_object, 2, debug=False)


def print_scene_nodes(fbx_scene, indent):
    for i in range(fbx_scene.GetNodeCount()):
        node = fbx_scene.GetNode(i)
        msg = "  " * indent
        msg += node.GetName()
        print msg


def print_scene_objects(fbx_scene, indent):
    """Print only instances of FbxObject, ie no subclass instances.
    Notes: not easy?!
    """
    criteria = fbx.FbxCriteria()

    if False:
        node_criteria = criteria.ObjectType(fbx.FbxNode.ClassId)
        # get everything that isn't a node
        # less than ideal method
        # means we can't use GetSrcObject with indices matching that of this
        # list
        nodes = []
        for i in range(fbx_scene.GetNodeCount()):
            node = fbx_scene.GetNode(i)
            nodes.append(node)

        not_nodes = []
        for i in range(fbx_scene.GetSrcObjectCount()):
            fbx_object = fbx_scene.GetSrcObject(i)
            if fbx_object not in nodes:
                not_nodes.append(fbx_object)

        for fbx_object in not_nodes:
            msg = "  " * indent
            msg += fbx_object.GetName()
            print msg
    else:
        # in cpp the criteria class provides a method
        # to query if something is not of a specific type
        # sadly this method does not seem to be present in python
        # instead we can use the specific type

        object_criteria = fbx.FbxCriteria().ObjectType(
            fbx.FbxNode.ClassId
        )

#         print object_criteria.GetQuery()

        print "object class id: ", fbx.FbxObject.ClassId.GetName()

        print dir(fbx.FbxObject.ClassId)
        print dir(object_criteria)
        print fbx.FbxObject.ClassId.ClassInstanceDecRef()
        print fbx.FbxObject.ClassId.ClassInstanceIncRef()

        for i in range(fbx_scene.GetSrcObjectCount(object_criteria)):
            fbx_object = fbx_scene.GetSrcObject(object_criteria, i)
            msg = "  " * indent
            msg += fbx_object.GetName()
            print msg


def get_object_classes():
    """Returns a list of all subclasses of FbxObject that are available in python SDK
    """
    subclasses = []

    for i in dir(fbx):
        obj = getattr(fbx, i)

        if not isclass(obj):
            continue

        if not issubclass(obj, fbx.FbxObject):
            continue

        subclasses.append(obj)

    return subclasses


def print_by_type(fbx_scene, indent):
    for object_class in get_object_classes():

        msg = "  " * indent
        msg += str(object_class.__name__)
        print msg

        criteria = fbx.FbxCriteria().ObjectTypeStrict(
            object_class.ClassId
        )

        for i in range(
            fbx_scene.GetSrcObjectCount(criteria)
        ):
            src_object = fbx_scene.GetSrcObject(criteria, i)

            msg = "  " * (indent + 1)
            msg += src_object.GetName()

            print msg


def inspect_example_scene():
    """Test that our connections have been maintained.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    fbx_manager.SetIOSettings(io_settings)

    res = FbxCommon.LoadScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)

    # print debug
    print "\n Reloaded \n"

#     print "\nScene Nodes:"
#     print_scene_nodes(fbx_scene, 1)

    print "\nScene Objects:"

    print_by_type(fbx_scene, 1)


if __name__ == "__main__":
    export_example_scene()
    inspect_example_scene()
    print "done"
