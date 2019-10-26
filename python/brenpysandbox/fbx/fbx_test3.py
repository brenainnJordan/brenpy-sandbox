'''
Created on 11 Mar 2019

@author: Bren
'''

import fbx

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\camera_aim_test_001.fbx"

fbx_manager = fbx.FbxManager.Create()
fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

# Create a node for our camera in the scene.
lCameraNode = fbx.FbxNode.Create(fbx_scene, "cameraNode")

# Create a light.
lCamera = fbx.FbxCamera.Create(fbx_scene, "camera")

# Set the node attribute of the camera node.
lCameraNode.SetNodeAttribute(lCamera)

# Add the camera node to the root node in the scene.
lRootNode = fbx_scene.GetRootNode()
lRootNode.AddChild(lCameraNode)

# Once a camera has been created, it can be set as the scene's default camera. A scene must have its default camera set explicitly, even if there is only one camera in the scene.
# Set the scene's default camera.
fbx_scene.GetGlobalSettings().SetDefaultCamera(lCamera.GetName())
# Pointing a camera
# A camera can be forced to consistently point towards a specific target in the scene. To do this, the camera's node must have its target set using FbxNode::SetTarget(). The FbxMarker node attribute is used in the target node.
# Create a node to contain the marker. This will be our target node.
lTargetNode = fbx.FbxNode.Create(fbx_scene, "targetNode")

# Create a marker node attribute.
lMarker = fbx.FbxMarker.Create(fbx_scene, "cameraMarker")

# Set the marker as the target node's attribute.
lTargetNode.SetNodeAttribute(lMarker)

lTargetNode.LclTranslation.Set(
    fbx.FbxDouble3(25.0, 12.0, 0.0)
)

# Set our camera node's target.
lCameraNode.SetTarget(lTargetNode)


# export
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

print "done"
