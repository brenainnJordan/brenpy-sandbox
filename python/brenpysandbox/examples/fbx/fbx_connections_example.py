'''
Created on 7 Sep 2019

@author: Bren

From fbx docs:

    Connections are not strict in the sense that we allow any type of objects to connect to
    any other type of objects.
    
    The meaning of the connection is purely semantic.
    
    As of yet, we do not provide the functionality to validate if the connections made
    by the users are allowed or not.

'''
import os
import fbx
import FbxCommon

DUMP_DIR = r"D:\Repos\dataDump\brenrig"

TEST_EXPORT_FILE = os.path.join(
    DUMP_DIR,
    "fbx_connection_example_01.fbx"
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

    # there are two ways to add a node to the scene
    # but not under the root
    # either by manually creating a connection
    # or by calling AddNode()
    fbx_scene.ConnectSrcObject(node_1)
    fbx_scene.AddNode(node_2)

    node_2.AddChild(node_3)
    node_3.AddChild(node_4)

    # we can also add a child by creating a connection
    # in an fbx file, parent/child relationships are
    # represented as connections
    # it is not possible to create a connection
    node_4.ConnectSrcObject(node_5)

    # here we connect a node that is already a child of another node
    # fbx keeps both connections
    # and thinks that node_3 is a child of both node_1 and node_2
    node_1.ConnectSrcObject(node_3)

    # note that the first connected object is represented as the "parent"
    print "multiple parent debug: ", node_3.GetParent().GetName()

    # create some objects
    object_1 = fbx.FbxObject.Create(fbx_manager, "object_1")
    object_2 = fbx.FbxObject.Create(fbx_manager, "object_2")
    object_3 = fbx.FbxObject.Create(fbx_manager, "object_3")
    object_4 = fbx.FbxObject.Create(fbx_manager, "object_4")

    fbx_scene.ConnectSrcObject(object_1)
    fbx_scene.ConnectSrcObject(object_2)

    # note connecting again results in only a single connection
    fbx_scene.ConnectSrcObject(object_2)

    # note we can connect an object to another object
    # without connecting it to the scene
    # a scene connection will automatically be created
    object_2.ConnectSrcObject(object_3)

    # we can also connect objects to nodes
    # however FbxObjects will not be represented as children
    node_2.ConnectSrcObject(object_4)

    # just to be sure
    fbx_scene.ConnectSrcObject(object_2)

    # test collections
    # these don't seem to save correctly
    # basically because a collection the base class of document
    # and document is base class of fbxScene
    # meaning we can only save one at a time
    collection_object = fbx.FbxCollection.Create(
        fbx_manager, "test_collection"
    )

    fbx_scene.ConnectSrcObject(collection_object)

    collection_object.AddMember(object_1)

    collection_object_2 = fbx.FbxCollection.Create(
        fbx_manager, "test_collection_2"
    )

    fbx_scene.ConnectSrcObject(collection_object_2)

    collection_object_2.AddMember(object_1)

#     object_2.SetRuntimeClassId() # errors

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


def print_selection_sets(fbx_object, indent, debug=True):

    criteria = fbx.FbxCriteria().ObjectType(
        fbx.FbxSelectionSet.ClassId
    )

    for i in range(
        fbx_object.GetSrcObjectCount(criteria)
    ):
        src_object = fbx_object.GetSrcObject(criteria, i)

        msg = "  " * indent
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

    # get nodes under root node
#     print "RootNode"
#     print_children(fbx_scene.GetRootNode(), 1)

    print "Scene"
    print_connected(fbx_scene, 1)

    print "Scene connections only:"
    print_connected(fbx_scene, 1, recursive=False,
                    include_children=False, debug=False)

    print "Organised hierarchy:"
    print_organised_children(fbx_scene)

    print "Destinations:"
    print_destinations(fbx_scene, 1)

    print "Selection sets:"
    print_selection_sets(fbx_scene, 1)


if __name__ == "__main__":
    export_example_scene()
    inspect_example_scene()
    print "done"
