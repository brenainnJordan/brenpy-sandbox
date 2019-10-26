'''
Created on 28 Apr 2019

@author: Bren

Test FbxPropertyReference

'''

import fbx
import FbxCommon

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\fbx_property_reference_test1.fbx"


def create_scene():
    """Create a scene with some nodes, and properties with connections/references to other nodes.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # create root
    root_name = "root"
    root_attr = fbx.FbxSkeleton.Create(fbx_manager, root_name)
    root_attr.SetSkeletonType(fbx.FbxSkeleton.eRoot)

    root_node = fbx.FbxNode.Create(fbx_manager, root_name)
    root_node.SetNodeAttribute(root_attr)

    # create some nodes
    node_1 = fbx.FbxNode.Create(fbx_manager, "node1")
    node_2 = fbx.FbxNode.Create(fbx_manager, "node2")
    node_3 = fbx.FbxNode.Create(fbx_manager, "node3")

    # note that when importing into Maya,
    # nodes without attributes default to joints
    # however they also do not hold property values
    #
    # if attr is skeleton or null, properties hold values correctly

#     node_2_attr = fbx.FbxSkeleton.Create(fbx_manager, "node2")
#     node_2_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)
    node_2_attr = fbx.FbxNull.Create(fbx_manager, "node2")
    node_2_attr.Look.Set(fbx.FbxNull.eNone)
#     node_2_attr.Look.Set(fbx.FbxNull.eCross) # locator shape
    node_2.SetNodeAttribute(node_2_attr)

    # create some objects
    object_1 = fbx.FbxObject.Create(fbx_manager, "object1")
    object_2 = fbx.FbxObject.Create(fbx_manager, "object2")
    object_3 = fbx.FbxObject.Create(fbx_manager, "object3")

    # create hierachy
    fbx_scene.GetRootNode().AddChild(root_node)
    root_node.AddChild(node_1)
    root_node.AddChild(node_2)
    root_node.AddChild(node_3)

    # connect objects to scene
    fbx_scene.ConnectSrcObject(object_1)
    fbx_scene.ConnectSrcObject(object_2)
    fbx_scene.ConnectSrcObject(object_3)

    # modify some data
    node_1.LclTranslation.Set(
        fbx.FbxDouble3(50.0, 0.0, 0.0)
    )

    # note that fbx.FbxReferenceDT properties do not import into Maya
    # create some references
    ref_prop = fbx.FbxProperty.Create(
        node_2, fbx.FbxReferenceDT, "testReferenceProperty"
    )

    ref_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    ref_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    ref_prop.ConnectSrcObject(node_1)

    # create some references with wrong property type
    # note that fbx.FbxDouble2DT properties do not import into Maya
    ref_dbl2_prop = fbx.FbxProperty.Create(
        node_2, fbx.FbxDouble2DT, "testReferenceDbl2Property"
    )
    ref_dbl2_prop.Set(19.0)
    ref_dbl2_prop.ConnectSrcObject(node_1)
    ref_dbl2_prop.ConnectSrcObject(node_3)
    ref_dbl2_prop.ConnectSrcObject(object_2)
    ref_dbl2_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    ref_dbl2_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    # dbl3
    # imports into maya correctly
    ref_dbl3_prop = fbx.FbxProperty.Create(
        node_2, fbx.FbxDouble3DT, "testReferenceDbl3Property"
    )

    ref_dbl2_prop.ConnectSrcObject(node_1)
    ref_dbl2_prop.ConnectSrcObject(node_3)
    ref_dbl2_prop.ConnectSrcObject(object_2)
    ref_dbl3_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    ref_dbl3_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)
    ref_dbl3_prop.Set(19.0)

    # dbl
    # note that while this property is imported into maya,
    # the property connection is NOT reproduced as a maya connection.
    ref_dbl_prop = fbx.FbxProperty.Create(
        node_2, fbx.FbxDoubleDT, "testReferenceDblProperty"
    )
    ref_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    ref_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    ref_dbl_prop.Set(15.6)
    ref_dbl_prop.ConnectSrcProperty(ref_dbl2_prop)

    print "done"
    return fbx_manager, fbx_scene


def inspect_scene(fbx_manager, fbx_scene):
    """Find property references.
    """
    # find node 2
    node_2 = fbx_scene.FindNodeByName("node2")

    # find reference property
    print "ref_prop..."
    ref_prop = node_2.FindProperty("testReferenceProperty")
    print ref_prop.IsValid()

    # get connected node (should be node_1)
    print "SrcCount: ", ref_prop.GetSrcObjectCount()
    node_1 = ref_prop.GetSrcObject(0)
    print node_1.GetName()

    # find reference property
    print "ref_dbl_prop..."
    ref_dbl2_prop = node_2.FindProperty("testReferenceDbl2Property")
    print ref_dbl2_prop.IsValid()

    # get connected node (should be node_1)
    print "SrcCount: ", ref_dbl2_prop.GetSrcObjectCount()
    print ref_dbl2_prop.GetSrcObject(0).GetName()
    print ref_dbl2_prop.GetSrcObject(1).GetName()
    print ref_dbl2_prop.GetSrcObject(2).GetName()
    print list(fbx.FbxPropertyDouble2(ref_dbl2_prop).Get())

    # find connected property
    ref_dbl_prop = node_2.FindProperty("testReferenceDblProperty")
    print ref_dbl_prop.IsValid()

    # note that the value of the connected property does not change
    print fbx.FbxPropertyDouble1(ref_dbl_prop).Get()
    print ref_dbl_prop.GetSrcProperty(0).GetName()

    print list(fbx.FbxPropertyDouble2(
        ref_dbl_prop.GetSrcProperty(0)
    ).Get())


def import_scene():
    """Import fbx file and find property references.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # create importer objects
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    fbx_manager.SetIOSettings(io_settings)
    fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")

    # Use the first argument as the filename for the importer.
    try:
        fbx_importer.Initialize(
            TEST_EXPORT_FILE, -1, fbx_manager.GetIOSettings()
        )
    except Exception as err:
        msg = "Call to FbxImporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            fbx_importer.GetStatus().GetErrorString()
        )
        print msg
        raise err

    # import file into scene
    fbx_importer.Import(fbx_scene)
    fbx_importer.Destroy()

    # get nodes
    inspect_scene(fbx_manager, fbx_scene)

    # cleanup
    fbx_manager.Destroy()
    del fbx_manager, fbx_scene

    print "import done"


if __name__ == "__main__":

    fbx_manager, fbx_scene = create_scene()

    res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)

    import_scene()
