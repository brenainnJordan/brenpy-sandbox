'''
Created on 6 Mar 2019

@author: Bren

Python/CPP SDK
https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2019-2

fbx viewer
https://www.autodesk.com/products/fbx/fbx-review

fbx archives
https://www.autodesk.com/developer-network/platform-technologies/fbx-converter-archives

fbx docs
https://download.autodesk.com/us/fbx/20112/fbx_sdk_help/index.html?url=WS1a9193826455f5ff453265c9125faa23bbb5fe8.htm,topicNumber=d0e8312
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_getting_started_your_first_fbx_sdk_program_html
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_scripting_with_python_fbx_using_python_fbx_with_eclipse_html

lib
C:\Program Files\Autodesk\FBX\FBX Python SDK\2019.2\lib\Python27_x64

tuts
http://awforsythe.com/tutorials

list of python classes
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_scripting_with_python_fbx_list_of_python_fbx_classes_html

interesting to note the file structure:
https://help.autodesk.com/view/FBX/2017/ENU/?guid=__cpp_ref_fbxnodeattribute_8h_source_html

'''


import fbx


def get_fbx_enums():
    for i in dir(fbx):
        if i.startswith("e"):
            print i


test_file = r"C:\Users\Bren\Desktop\tests\joints_fbx_ascii_test_001.fbx"

# Create the required FBX SDK data structures.
fbx_manager = fbx.FbxManager.Create()

# Create the IO settings object.
io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
# or simply "IOSRoot") as this is define in cpp as #define IOSROOT   "IOSRoot"

fbx_manager.SetIOSettings(io_settings)

# Create an importer using the SDK manager.
fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")


# Use the first argument as the filename for the importer.
try:
    fbx_importer.Initialize(
        test_file, -1, fbx_manager.GetIOSettings()
    )
except Exception as err:
    msg = "Call to FbxImporter::Initialize() failed.\n"
    msg += "Error returned: {0}".format(
        fbx_importer.GetStatus().GetErrorString()
    )
    print msg
    raise err

#     if(!lImporter->Initialize(lFilename, -1, lSdkManager->GetIOSettings())) {
#         printf("Call to FbxImporter::Initialize() failed.\n");
#         printf("Error returned: %s\n\n", lImporter->GetStatus().GetErrorString());
#         exit(-1);

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


def print_node(fbx_node):
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
        pass

    # property test
#     prop = fbx_node.FindProperty("LclTranslation")
#     print "radius: ", prop.IsValid()
#     for i in dir(prop):
#         if "data" in i.lower():
#             print i

    prop = fbx_node.GetFirstProperty()

    while prop.IsValid():
        #         for i in dir(prop):
        #             print i
        #
        #         raise

        print "prop {0} {1}".format(
            prop.GetName(),
            prop.GetPropertyDataType().GetType()
            #             prop.Get()
        )

        prop = fbx_node.GetNextProperty(prop)

    # Recursively print the children.
    for i in range(fbx_node.GetChildCount()):
        print_node(fbx_node.GetChild(i))


fbx_root_node = fbx_scene.GetRootNode()

if fbx_root_node:
    for i in range(fbx_root_node.GetChildCount()):
        # print fbx_root_node.GetChild(i)
        print_node(fbx_root_node.GetChild(i))

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
