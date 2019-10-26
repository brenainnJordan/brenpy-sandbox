"""
Stuff.

TODO

Load maya exported curve via sdk and inspect knots etc.
Try re-exporting it.
Try copying properties to new curve node.
Figure shit out yo!

cpp example of how to set knotvector via pointers?!

    double lUKnotVector[] = { -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0 };
    memcpy(lNurbs->GetUKnotVector(), lUKnotVector, lNurbs->GetUKnotCount()*sizeof(double));

    double lVKnotVector[] = { 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0, 4.0, 4.0 };
    memcpy(lNurbs->GetVKnotVector(), lVKnotVector, lNurbs->GetVKnotCount()*sizeof(double));


"""

import fbx
import FbxCommon

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\fbx_nurbs_test_001.fbx"


def create_nurbs_curve():
    """Create nurbs curve example.

    https://help.autodesk.com/view/FBX/2017/ENU/?guid=__cpp_ref_class_fbx_nurbs_curve_html

    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # create curve

    M = 4  # degree/order
    N = 10  # number of control points

    crv_node = fbx.FbxNode.Create(fbx_manager, "test_curve")
    crv_attr = fbx.FbxNurbsCurve.Create(fbx_manager, "")
    crv_node.SetNodeAttribute(crv_attr)

    pOrder = M

#     crv_attr.SetStep(16)
    crv_attr.SetOrder(pOrder)

    pCount = N
    pVType = fbx.FbxNurbsCurve.eOpen
#     pVType = fbx.FbxNurbsCurve.ePeriodic

    crv_attr.InitControlPoints(pCount, pVType)
#     crv_attr.InitTangents()
#     crv_attr.InitNormals()
#     crv_attr.SetDimension(fbx.FbxNurbsCurve.e3D)  # or e2D

    # modify curve
    for i in range(N):
        crv_attr.SetControlPointAt(
            fbx.FbxVector4(i,  0.0,  50.0, 1.0),
            i
        )
    print crv_attr.IsRational()

    points = crv_attr.GetControlPoints()

    for point in points:
        print point

#     for i in range(4, N - 4):
#         crv_attr.SetControlPointAt(
#             fbx.FbxVector4(i,  0.0,  50.0, 0.0),
#             i
#         )
#
#     for i in range(N - 4, N):
#         crv_attr.SetControlPointAt(
#             fbx.FbxVector4(N - 4,  0.0,  50.0, 0.0),
#             i
#         )
#
#         crv_attr.SetControlPointNormalAt(
#             fbx.FbxVector4(1.0,  1.0,  1.0, 1.0),
#             i
#         )
#
#     for i in dir(crv_attr):
#         print i

    knots_a = crv_attr.GetKnotVector()
    knots_b = crv_attr.GetKnotVector()
    print knots_a
    print knots_a == knots_b
    print knots_a is knots_b

#     crv_attr.SetKnotVector()

    # evaluate curve
#     crv_line = crv_attr.TessellateCurve(16)
#     print help(crv_attr.ConvertDirectToIndexToDirect)
#     print help(crv_attr.Localize)

    # add curve to scene
    fbx_scene.GetRootNode().AddChild(crv_node)

    # save file using FbxCommon
    res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)


if __name__ == "__main__":
    create_nurbs_curve()
    print "done"
