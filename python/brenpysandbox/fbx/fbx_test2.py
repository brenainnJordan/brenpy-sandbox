'''
Created on 10 Mar 2019

@author: Bren
'''

import fbx

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\joints_aim_test_001.fbx"


def test(fbx_manager):
    # create root
    #     root_name = "root"
    #     root_attr = fbx.FbxSkeleton.Create(fbx_manager, root_name)
    #     root_attr.SetSkeletonType(fbx.FbxSkeleton.eRoot)
    #
    #     root_node = fbx.FbxNode.Create(fbx_manager, root_name)
    #     root_node.SetNodeAttribute(root_attr)

    # create joint0
    joint0_name = "joint0"
    joint0_attr = fbx.FbxSkeleton.Create(fbx_manager, joint0_name)
    joint0_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)

    joint0_node = fbx.FbxNode.Create(fbx_manager, joint0_name)
    joint0_node.SetNodeAttribute(joint0_attr)

    # create joint1
    joint1_name = "joint1"
    joint1_attr = fbx.FbxSkeleton.Create(fbx_manager, joint1_name)
    joint1_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)

    joint1_node = fbx.FbxNode.Create(fbx_manager, joint1_name)
    joint1_node.SetNodeAttribute(joint1_attr)

    joint1_node.LclTranslation.Set(
        fbx.FbxDouble3(10.0, 0.0, 0.0)
    )

    joint0_node.AddChild(joint1_node)

    # create joint2
    joint2_name = "joint2"
    joint2_attr = fbx.FbxSkeleton.Create(fbx_manager, joint2_name)
    joint2_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)

    joint2_node = fbx.FbxNode.Create(fbx_manager, joint2_name)
    joint2_node.SetNodeAttribute(joint2_attr)

    joint2_node.LclTranslation.Set(
        fbx.FbxDouble3(25.0, 12.0, 0.0)
    )

    # aim joint 0 at joint 2 (think this only works for cameras)
    joint0_node.SetTarget(joint2_node)
    print joint0_node.GetTarget()
    print joint2_node.LookAtProperty.Get() == joint0_node.GetTarget()

    lCameraNode = fbx.FbxNode.Create(fbx_manager, "cameraNode")
    lCamera = fbx.FbxCamera.Create(fbx_manager, "camera")
    lCameraNode.SetNodeAttribute(lCamera)
    lCameraNode.SetTarget(joint2_node)

    return joint0_node, joint2_node, lCameraNode


def export_skel():
    """Create a manager, scene, skel and export file.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")
    root_node, joint2_node, lCameraNode = test(fbx_manager)

    fbx_scene.GetRootNode().AddChild(root_node)
    fbx_scene.GetRootNode().AddChild(joint2_node)
    fbx_scene.GetRootNode().AddChild(lCameraNode)

    if False:
        # save file using FbxCommon
        #         res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)
        pass
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


if __name__ == "__main__":
    export_skel()

    print "done"
