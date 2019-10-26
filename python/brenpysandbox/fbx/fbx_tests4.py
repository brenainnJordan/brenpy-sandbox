'''
Created on 12 Mar 2019

@author: Bren

http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_cpp_ref_annotated_html

relevent docs:
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_nodes_and_scene_graph_fbx_scenes_merging_two_scenes_html

'''

import fbx
import FbxCommon

# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_fbx_ascii_test_001.fbx"
# TEST_FILE = r"D:\Jobs\Centroid\Ideal_T_pose_weapon_RollBones.fbx"
# TEST_FILE = r"D:\Jobs\Centroid\IRON MAN Characterised PRE-VIS.fbx"
# TEST_FILE = r"D:\Jobs\Centroid\THARK TEST.fbx"

TEST_FILE = r"C:\Users\Bren\Desktop\tests\rig_to_test_002.fbx"
TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\rig_manip_test_001.fbx"


fbx_manager = fbx.FbxManager.Create()
fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
fbx_manager.SetIOSettings(io_settings)

FbxCommon.LoadScene(fbx_manager, fbx_scene, TEST_FILE)

# list all meshes in the scene via "connections"
mesh_count = fbx_scene.GetSrcObjectCount(
    # includes classes that derive from specified class:
    #     fbx.FbxCriteria.ObjectType(fbx.FbxMesh.ClassId)
    # specified class only:
    fbx.FbxCriteria.ObjectTypeStrict(fbx.FbxMesh.ClassId)
)

for i in range(mesh_count):
    mesh_node = fbx_scene.GetSrcObject(
        fbx.FbxCriteria.ObjectTypeStrict(fbx.FbxMesh.ClassId),
        i
    )
    print mesh_node.GetNode().GetName()


# find a node in the scene

#########
# *** IMPORTANT NOTE ****
# something in Ideal_T_pose_weapon_RollBones.fbx"
# doesnt allow joints to be rotated etc.
# TODO find out why
########

root = fbx_scene.GetRootNode()

ideal_node = root.GetChild(1)
ideal_node.SetName("poop")
ideal_node.LclRotation.Set(
    fbx.FbxDouble3(10, 15, 45)
)

found_node = root.FindChild("LeftForeArm")
if found_node:
    print found_node.GetName()
    found_node.SetRotationActive(True)
    print found_node.LclRotation.Set(
        fbx.FbxDouble3(45, 30, 90)
    )
    found_node.LclTranslation.Set(
        fbx.FbxDouble3(45, 300, 90)
    )

# test
joint2_name = "joint2"
joint2_attr = fbx.FbxSkeleton.Create(fbx_manager, joint2_name)
joint2_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)

joint2_node = fbx.FbxNode.Create(fbx_manager, joint2_name)
joint2_node.SetNodeAttribute(joint2_attr)

joint2_node.LclTranslation.Set(
    fbx.FbxDouble3(25.0, 0.0, 0.0)
)

joint2_node.LclRotation.Set(
    fbx.FbxDouble3(0.0, 0.0, 45.0)
)
root.AddChild(joint2_node)
# save new file
# res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)
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

# cleanup
fbx_manager.Destroy()
del fbx_manager, fbx_scene
