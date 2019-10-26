import math

import fbx
import FbxCommon

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\fbx_nurbs_test_003.fbx"
UKnotVector = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0,
               4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0)
VKnotVector = (0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0, 4.0, 4.0)


# Create a sphere.
def CreateNurbs(pSdkManager, pName):
    """Taken from fbx sdk sample "ExportScene02.py"
    """
    lNurbs = fbx.FbxNurbs.Create(pSdkManager, pName)
    lNurbs.SetOrder(4, 4)
    lNurbs.SetStep(2, 2)
    lNurbs.InitControlPoints(8, fbx.FbxNurbs.ePeriodic, 7, fbx.FbxNurbs.eOpen)
    lNurbs.SetUKnotVector(list(UKnotVector))
    lNurbs.SetVKnotVector(list(VKnotVector))

    lScale = 20.0
    lPi = 3.14159
    lYAngle = (90.0, 90.0, 52.0, 0.0, -52.0, -90.0, -90.0)
    lRadius = (0.0, 0.283, 0.872, 1.226, 0.872, 0.283, 0.0)

    for i in range(7):
        for j in range(8):
            lX = lScale * lRadius[i] * math.cos(lPi / 4 * j)
            lY = lScale * math.sin(2 * lPi / 360 * lYAngle[i])
            lZ = lScale * lRadius[i] * math.sin(lPi / 4 * j)
            lNurbs.SetControlPointAt(
                fbx.FbxVector4(lX, lY, lZ, 1.0), 8 * i + j)

    # Create Layer 0 where material and texture will be applied
    if not lNurbs.GetLayer(0):
        lNurbs.CreateLayer()

    lNurbsNode = fbx.FbxNode.Create(pSdkManager, pName)
    lNurbsNode.SetNodeAttribute(lNurbs)
    return lNurbsNode


def export_nurbs():
    """Create nurbs example.

    https://help.autodesk.com/view/FBX/2017/ENU/?guid=__cpp_ref_class_fbx_nurbs_curve_html

    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # create nurbs
    nurbs_node = CreateNurbs(fbx_manager, "test_surface")

    # add curve to scene
    fbx_scene.GetRootNode().AddChild(nurbs_node)

    # save file using FbxCommon
    res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)


if __name__ == "__main__":
    export_nurbs()
    print "done"
