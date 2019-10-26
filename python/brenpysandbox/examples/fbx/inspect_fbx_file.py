'''
Python version of fbx cpp example "Your first FBX SDK program"
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_getting_started_your_first_fbx_sdk_program_html

Created on 6 Mar 2019

@author: Bren

Notes:
Python/CPP SDK
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_cpp_ref_annotated_html

fbx viewer
https://www.autodesk.com/products/fbx/fbx-review

lib
C:\Program Files\Autodesk\FBX\FBX Python SDK\2019.2\lib\Python27_x64

'''

import os
import fbx

SRC_DATA_DIR = r"D:\Repos\dataDump\fbx_tests"
TEST_FILE = r"joints_fbx_ascii_test_001.fbx"
# TEST_FILE = r"maya_constraints_test_001.fbx"
# TEST_FILE = r"constraints_test_001.fbx"

DUMP_DIR = r"D:\Repos\dataDump\brenrig"

TEST_FILE = os.path.join(
    DUMP_DIR,
    "fbx_prototype_01_session_002.fbx"
)

TEST_FILE = os.path.join(
    DUMP_DIR,
    "fbx_prototype_01_output_002.fbx"
)

ATTRIBUTE_NAMES = {
    fbx.FbxNodeAttribute.eUnknown: "unidentified",
    fbx.FbxNodeAttribute.eNull: "null",
    fbx.FbxNodeAttribute.eMarker: "marker",
    fbx.FbxNodeAttribute.eSkeleton: "skeleton",
    fbx.FbxNodeAttribute.eMesh: "mesh",
    fbx.FbxNodeAttribute.eNurbs: "nurbs",
    fbx.FbxNodeAttribute.ePatch: "patch",
    fbx.FbxNodeAttribute.eCamera: "camera",
    fbx.FbxNodeAttribute.eCameraStereo: "stereo",
    fbx.FbxNodeAttribute.eCameraSwitcher: "camera switcher",
    fbx.FbxNodeAttribute.eLight: "light",
    fbx.FbxNodeAttribute.eOpticalReference: "optical reference",
    fbx.FbxNodeAttribute.eOpticalMarker: "marker",
    fbx.FbxNodeAttribute.eNurbsCurve: "nurbs curve",
    fbx.FbxNodeAttribute.eTrimNurbsSurface: "trim nurbs surface",
    fbx.FbxNodeAttribute.eBoundary: "boundary",
    fbx.FbxNodeAttribute.eNurbsSurface: "nurbs surface",
    fbx.FbxNodeAttribute.eShape: "shape",
    fbx.FbxNodeAttribute.eLODGroup: "lodgroup",
    fbx.FbxNodeAttribute.eSubDiv: "subdiv",
}


def print_attribute(fbx_attribute):
    """Print user readable name for node attribute.

    Note:
        fbx attributes are not the same as properties.
        attributes describe the type of node.

        eg.
        a skeleton node is a FbxNode with attribute type of
        fbx.FbxNodeAttribute.eSkeleton

    """
    if not fbx_attribute:
        return

    type_name = ATTRIBUTE_NAMES[
        fbx_attribute.GetAttributeType()
    ]

    attr_name = fbx_attribute.GetName()

    # Note: to retrieve the character array of a FbxString, use its Buffer()
    # method.
#     msg = "\t\t{0} {1}".format(type_name.Buffer(), attr_name.Buffer())

    # not neccesary to use buffer in python
    # TODO find out why
    msg = "\tAttribute type:{0}\n\tAttribute name:{1}".format(
        type_name, attr_name
    )

    print msg


def print_node(fbx_node):
    """Print some things about this FbxNode

    Note:
        FbxNode is the equivalent of the Maya Transform base class.
        It has a hierarchical structure and transform data by default.

    """

    node_name = fbx_node.GetName()
    translation = fbx_node.LclTranslation.Get()
    rotation = fbx_node.LclRotation.Get()
    scaling = fbx_node.LclScaling.Get()

    # Print the contents of the node.
    msg = "{0}:\n\tTranslation: {1}\n\tRotation: {2}\n\tScaling: {3}"
    msg = msg.format(
        node_name,
        list(translation),
        list(rotation),
        list(scaling)
    )
    print msg

    # Print the node's attributes.
    for i in range(fbx_node.GetNodeAttributeCount()):
        fbx_attribute = fbx_node.GetNodeAttributeByIndex(i)
        print_attribute(fbx_attribute)

    print "\n"

    # find all connections
    src_count = fbx_node.GetSrcObjectCount()

    for i in range(src_count):
        src = fbx_node.GetSrcObject(i)
#         print p_cons.GetNode().GetName()
        print "{} src: '{}' {}".format(fbx_node.GetName(), src.GetName(), src)

    dst_count = fbx_node.GetDstObjectCount()

    for i in range(dst_count):
        dst = fbx_node.GetDstObject(i)
        print "{} dst: '{}' {}".format(fbx_node.GetName(), dst.GetName(), dst)

    # Recursively print the children.
    for i in range(fbx_node.GetChildCount()):
        print_node(fbx_node.GetChild(i))


def inspect_fbx_file(file_path):
    """Import (load) fbx file into memory and print some stuff about it.
    """
    # Create the required FBX SDK data structures.
    fbx_manager = fbx.FbxManager.Create()

    # Create the IO settings object.
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    # or simply "IOSRoot") as this is define in cpp as #define IOSROOT
    # "IOSRoot"

    fbx_manager.SetIOSettings(io_settings)

    # Create an importer using the SDK manager.
    fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")

    # Use the first argument as the filename for the importer.
    try:
        fbx_importer.Initialize(
            file_path, -1, fbx_manager.GetIOSettings()
        )
    except Exception as err:
        msg = "Call to FbxImporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            fbx_importer.GetStatus().GetErrorString()
        )
        print msg
        raise err

    # The FbxImporter object populates a provided FbxScene object with the elements contained in the FBX file.
    # Observe that an empty string is passed as the second parameter in the FbxScene::Create() function.
    # Objects created in the FBX SDK can be given arbitrary, non-unique names,
    # that allow the user or other programs to identify the object after it is exported.
    # After the FbxScene is populated, the FbxImporter can be safely destroyed.

    # Create a new scene so that it can be populated by the imported file.
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # Import the contents of the file into the scene.
    fbx_importer.Import(fbx_scene)

    # The file is imported, so get rid of the importer.
    fbx_importer.Destroy()

    # Print the nodes of the scene and their attributes recursively.
    # Note that we are not printing the root node because it should
    # not contain any attributes.

    fbx_root_node = fbx_scene.GetRootNode()

    if fbx_root_node:
        for i in range(fbx_root_node.GetChildCount()):
            # print fbx_root_node.GetChild(i)
            print_node(fbx_root_node.GetChild(i))

    # find all connections
    print "\nScene source connections:..."
    src_count = fbx_scene.GetSrcObjectCount()

    for i in range(src_count):
        src = fbx_scene.GetSrcObject(i)
#         print p_cons.GetNode().GetName()
        print "scene src: '{}', {}".format(src.GetName(), src)

    print "\nScene destination connections:..."
    dst_count = fbx_scene.GetDstObjectCount()

    for i in range(dst_count):
        dst = fbx_scene.GetDstObject(i)
        print "scene dst: '{}' {}".format(dst.GetName(), dst)

    ### CLEANUP ###
    #
    # Destroy the fbx manager explicitly, which recursively destroys
    # all the objects that have been created with it.
    fbx_manager.Destroy()
    #
    # Once the memory has been freed, it is good practice to delete
    # the currently invalid references contained in our variables.
    del fbx_manager, fbx_scene

    print "done"


if __name__ == "__main__":
    inspect_fbx_file(
        os.path.join(SRC_DATA_DIR, TEST_FILE)
    )
