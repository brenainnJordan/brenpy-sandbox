'''Example of how to trick Fbx into thinking a node is a child of multiple nodes.

This is probably a very bad thing, this example reveals the issues.

Ideally we would like to represent node hierarchy by using connections only.
However the order of object connections does not appear to be reliable.
While not exactly arbitrary, fbx seems to do some of it's own organisation
upon export.
This directly affects the order of connections after loading.

For example Scene connection is last after first parenting a node,
but is then first after reloading. 

The moral of this example is to always use AddChild() and never create
direct node to node connections.

Use node-property connections instead to represent non-hierarhcical relationships.

Created on 8 Sep 2019

@author: Bren
'''

import os
import fbx
import FbxCommon

DUMP_DIR = r"D:\Repos\dataDump\brenrig"

TEST_EXPORT_FILE = os.path.join(
    DUMP_DIR,
    "fbx_multiple_parent_example_01.fbx"
)


def create_example_scene(fbx_manager):
    """Create a scene containing some example node and object connections
    """
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "test_scene")

    # create some nodes
    node_1 = fbx.FbxNode.Create(fbx_manager, "node_1")
    node_2 = fbx.FbxNode.Create(fbx_manager, "node_2")
    node_3 = fbx.FbxNode.Create(fbx_manager, "node_3")
    node_4 = fbx.FbxNode.Create(fbx_manager, "node_4")
    node_5 = fbx.FbxNode.Create(fbx_manager, "node_5")

    # organise under rootNode
    fbx_scene.GetRootNode().AddChild(node_1)
    fbx_scene.GetRootNode().AddChild(node_2)
    node_2.AddChild(node_3)
    node_3.AddChild(node_4)
    node_1.AddChild(node_5)

    # also add node 5 as child of node_2
    # note that using AddChild() first removes
    # the connection to the current parent
    node_2.AddChild(node_5)

    # however by creating a connection manually
    # fbx thinks that node_5 is a child of both node_1 and node_2
    node_1.ConnectSrcObject(node_5)

    # however calling GetParent() reveals that
    # node_2 is still the "parent"
    # however this is a massive red-herring
    # as this changes upon reloading

    # return scene
    return fbx_scene


def export_example_scene():
    """Create a manager, scene, skel and export file.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = create_example_scene(fbx_manager)

    print "\n Pre-save \n"
    print "Destinations:"
    print_destinations(fbx_scene, 1)

    print "\n"

    print "Hierarchy:"
    print_children(fbx_scene.GetRootNode(), 1, debug=True)

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

    print "\nfile exported: {}".format(TEST_EXPORT_FILE)


def print_children(node, indent, debug=True):
    for i in range(node.GetChildCount()):
        child_node = node.GetChild(i)

        msg = "  " * indent
        msg += child_node.GetName()

        if debug:
            msg += " (child of {})".format(child_node.GetParent().GetName())

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

    print "Destinations:"
    print_destinations(fbx_scene, 1)

    print "\n"

    print "Hierarchy:"
    print_children(fbx_scene.GetRootNode(), 1, debug=True)


if __name__ == "__main__":
    export_example_scene()
    inspect_example_scene()
    print "done"
