"""
Stuff.

TODO

"""

import fbx
import FbxCommon

TEST_IMPORT_FILE = r"C:\Users\Bren\Desktop\tests\maya_surface_test_001.fbx"
TEST_EXPORT_FILE_1 = r"C:\Users\Bren\Desktop\tests\fbx_maya_surface_test_001.fbx"
TEST_EXPORT_FILE_2 = r"C:\Users\Bren\Desktop\tests\fbx_maya_surface_test_002.fbx"


def import_surface_test_1():
    """

    """
    fbx_manager = fbx.FbxManager.Create()
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)

    fbx_manager.SetIOSettings(io_settings)
    fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")

    fbx_importer.Initialize(
        TEST_IMPORT_FILE, -1, fbx_manager.GetIOSettings()
    )

    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")
    fbx_importer.Import(fbx_scene)
    fbx_importer.Destroy()

    # find surface
    surface_node = fbx_scene.FindNodeByName("nurbsPlane1")

    if not surface_node:
        raise Exception("surface node not found")

    nurbs_attr = surface_node.GetNodeAttribute()

    if not isinstance(nurbs_attr, (fbx.FbxNurbs, fbx.FbxNurbsSurface)):
        raise Exception("surface node is not FbxNurbs or fbx.FbxNurbsSurface")

    # get curve data
    if True:
        u_knots = nurbs_attr.GetUKnotVector()
        v_knots = nurbs_attr.GetVKnotVector()
        points = nurbs_attr.GetControlPoints()

        print u_knots
        print v_knots

        print nurbs_attr.GetControlPointsCount()

        for point in points:
            print point
    return
#
#     # create new scene
#     new_scene = fbx.FbxScene.Create(fbx_manager, "ExportScene")
#
#     # clone curve to new scene
#     clone_node = fbx.FbxNode.Create(fbx_manager, "clone_curve")
#
#     clone_attr = curve_attr.Clone(
#         # Changes to original object propagate to clone. Changes to clone do not propagate to original.
#         # eREFERENCE_CLONE
#         # A deep copy of the object.
#         # Changes to either the original or clone do not propagate to each
#         # other.)
#         fbx.FbxObject.eDeepClone,
#         new_scene
#     )
#
#     clone_node.SetNodeAttribute(clone_attr)
#     new_scene.GetRootNode().AddChild(clone_node)
#
#     print "clone: ", clone_attr
#
#     # check cloned data
#     knots = clone_attr.GetKnotVector()
#     points = clone_attr.GetControlPoints()
#
#     print knots
#     for point in points:
#         print point
#
#     # move curve to new scene
#
#     # remove curve from imported scene
#     fbx_scene.GetRootNode().RemoveChild(curve_node)
#     fbx_scene.DisconnectSrcObject(curve_node)
#     fbx_scene.DisconnectSrcObject(curve_attr)
#
#     # add to new scene
#     new_scene.GetRootNode().AddChild(curve_node)
#
#     # manipulate curve
#     curve_attr.SetControlPointAt(
#         fbx.FbxVector4(0.0,  0.0,  50.0, 1.0),
#         2
#     )
#
#     # export new scene
#     res = FbxCommon.SaveScene(fbx_manager, new_scene, TEST_EXPORT_FILE_1)
#
#     print res
#
#     return True

#
# def import_curve_test_2():
#     # import curve
#     fbx_manager = fbx.FbxManager.Create()
#     io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
#
#     fbx_manager.SetIOSettings(io_settings)
#     fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")
#
#     fbx_importer.Initialize(
#         TEST_IMPORT_FILE, -1, fbx_manager.GetIOSettings()
#     )
#
#     fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")
#     fbx_importer.Import(fbx_scene)
#     fbx_importer.Destroy()
#
#     # find curve
#     i_curve_node = fbx_scene.FindNodeByName("curve1")
#     i_curve_attr = i_curve_node.GetNodeAttribute()
#
#     # create new scene and copy curve data to new curve node
#     new_scene = fbx.FbxScene.Create(fbx_manager, "ExportScene")
#
#     n_curve_node = fbx.FbxNode.Create(fbx_manager, "test_curve")
#     n_curve_attr = fbx.FbxNurbsCurve.Create(fbx_manager, "")
#     n_curve_node.SetNodeAttribute(n_curve_attr)
#
# #     crv_attr.SetStep(16)
#     n_curve_attr.SetOrder(
#         i_curve_attr.GetOrder()
#     )
#
#     n_curve_attr.InitControlPoints(
#         i_curve_attr.GetControlPointsCount(),
#         i_curve_attr.GetType()
#     )
#
#     for i, point in enumerate(i_curve_attr.GetControlPoints()):
#         n_curve_attr.SetControlPointAt(
#             point,
#             i
#         )
#
#     print n_curve_attr.ComputeBBox()
#
# #     crv_attr.InitTangents()
# #     crv_attr.InitNormals()
# #     crv_attr.SetDimension(fbx.FbxNurbsCurve.e3D)  # or e2D
#
#     # check curve data
#     knots = n_curve_attr.GetKnotVector()
#     points = n_curve_attr.GetControlPoints()
#
#     print knots
#     for point in points:
#         print point
#
#     # add to new scene
#     new_scene.GetRootNode().AddChild(n_curve_node)
#
#     # export new scene
#     res = FbxCommon.SaveScene(fbx_manager, new_scene, TEST_EXPORT_FILE_2)
#
#     print res
#
#     return True


if __name__ == "__main__":
    import_surface_test_1()
