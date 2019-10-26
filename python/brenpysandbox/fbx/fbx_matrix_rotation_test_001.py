'''
Created on 9 Jun 2019

@author: Bren

manipulate nodes rotations with various methods using matrices 

TODO figure out what I'm doing wrong with the scipy_rotation.from_dcm (direction cosines) method.

Turns out we need to transpose the matrix before sending to from_dcm,
but there's still differences between xyz eulers results and zyx etc.
Investigate further.

and/or continue to investigate other methods to calculate euler rotations from a matrix or direction vectors etc.

'''

import os
import sys

import numpy
from scipy.spatial.transform import Rotation as scipy_rotation

# temp hacky hack
for script_path in [
    r"D:\Repos\brenrig\python",
    r"D:\Repos\brenpy",
    r"D:\Repos\brenmy\python",
]:
    if script_path not in sys.path:
        sys.path.append(script_path)

import fbx
import FbxCommon

from bfbx.bfbxcore import fbxIO
reload(fbxIO)

from bfbx.bfbxcore import fbxData
reload(fbxData)

from bfbx.bfbxcore import fbxUtils
reload(fbxUtils)

# file globals
DUMP_DIR = r"D:\Repos\dataDump\fbx_tests"

EXPORT_FILEPATH = os.path.join(
    DUMP_DIR,
    "matrix_rotation_tests_001.fbx"
)


def create_scene():
    fbx_manager = fbx.FbxManager()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "prototype_session_scene")
    root_node = fbx_scene.GetRootNode()

    # create some nodes
    loc_1 = fbxUtils.create_locator("loc1", fbx_manager, root_node)
    loc_2 = fbxUtils.create_locator("loc2", fbx_manager, root_node)
    loc_3 = fbxUtils.create_locator("loc3", fbx_manager, root_node)

    # maniuplate locators
    mat_1 = fbx.FbxAMatrix()
    mat_1.SetT(
        fbx.FbxVector4(1, 2, 3, 0)
    )

    mat_1.SetR(
        fbx.FbxVector4(45, 0, 0, 0)
    )

    # inspect matrix values
    if False:
        print mat_1.GetRow(0)
        print mat_1.GetRow(1)
        print mat_1.GetRow(2)
        print mat_1.GetRow(3)

    # test scale
    if False:
        mat_1.SetS(
            fbx.FbxVector4(2, 2, 2, 0)
        )

        print mat_1.GetRow(0)
        print mat_1.GetRow(1)
        print mat_1.GetRow(2)
        print mat_1.GetRow(3)

    # set node values
    loc_1.LclTranslation.Set(
        fbx.FbxDouble4(*list(mat_1.GetT()))
    )

    loc_1.LclRotation.Set(
        fbx.FbxDouble4(*list(mat_1.GetR()))
    )

    # test "aim"
    if False:
        # the aim matrix method aint gonna work
        # cos we can only set rows using FbxMatrix
        # but we can't get Euler values from it
        # and we can't turn it into FbxAMatrix
        # so I guess we have to do it the hard way?
        mat_2 = fbx.FbxMatrix()

        mat_2.SetRow(0, fbx.FbxVector4(1, 0, 0, 0))
        mat_2.SetRow(1, fbx.FbxVector4(0, 1, 0, 0))
        mat_2.SetRow(2, fbx.FbxVector4(0, 0, 1, 0))
        mat_2.SetRow(3, fbx.FbxVector4(2, 0, 0, 1))

        mat_2a = mat_2 * fbx.FbxAMatrix()

        loc_2.LclTranslation.Set(
            fbx.FbxDouble4(*list(mat_2a.GetT()))
        )

        loc_2.LclRotation.Set(
            fbx.FbxDouble4(*list(mat_2a.GetR()))
        )

    # in theory this method should support rotation orders...?

    # euler aim (x - aim, y - up)
    x_aim_vector = fbx.FbxVector4(0.5, 0.1, 0.4, 0)
    y_up_vector = fbx.FbxVector4(-0.2, 1, 0.1, 0)

    # calculate vectors
    x_aim_vector.Normalize()
    y_up_vector.Normalize()
    z_norm_vector = x_aim_vector.CrossProduct(y_up_vector)
#     z_norm_vector = y_up_vector.CrossProduct(x_aim_vector)
    z_norm_vector.Normalize()
#     y_corrected_up_vector = x_aim_vector.CrossProduct(z_norm_vector)
    y_corrected_up_vector = z_norm_vector.CrossProduct(x_aim_vector)

    if False:
        # debugging
        print "aim ", x_aim_vector, x_aim_vector.Length()
        print "up ", y_up_vector, y_up_vector.Length()
        print "cor up ", y_corrected_up_vector, y_corrected_up_vector.Length()
        print "norm ", z_norm_vector, z_norm_vector.Length()

        print "np x", numpy.cross(
            [0, 1, 0],
            [0, 0, 1],
        )

        print "np y", numpy.cross(
            [0, 0, 1],
            [1, 0, 0],
        )

        print "np z", numpy.cross(
            [1, 0, 0],
            [0, 1, 0],
        )

    if False:
        # create scipy rotation object
        # using direction cosine matrix

        directions = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0]
        ]

        x_aim_cosines = [
            fbx.FbxVector4(*direction).DotProduct(
                x_aim_vector,
            ) for direction in directions
        ]

        y_up_cosines = [
            fbx.FbxVector4(*direction).DotProduct(
                y_up_vector,
            ) for direction in directions
        ]

        z_norm_cosines = [
            fbx.FbxVector4(*direction).DotProduct(
                z_norm_vector,
            ) for direction in directions
        ]

        print numpy.array([
            x_aim_cosines,
            y_up_cosines,
            z_norm_cosines
        ])

        print numpy.rad2deg([
            x_aim_cosines,
            y_up_cosines,
            z_norm_cosines
        ])

    sp_rot = scipy_rotation.from_dcm(
        #         # [0.0, 0.0, -17.46279830041399]
        #         numpy.rad2deg([
        #             x_aim_cosines,
        #             y_up_cosines,
        #             z_norm_cosines
        #         ])
        #
        #         #[0.0, 0.0, -13.101645932991731]
        numpy.array([
            list(x_aim_vector)[:3],
            list(y_up_vector)[:3],
            list(z_norm_vector)[:3]
        ]).transpose()
        # [0.0, 0.0, -13.101645932991731]
        #         numpy.array([
        #             x_aim_cosines,
        #             y_up_cosines,
        #             z_norm_cosines
        #         ])
    )

    poop_aim = sp_rot.as_euler('ZYX', degrees=True).tolist()
    euler_aim = sp_rot.as_euler('XYZ', degrees=True).tolist()

    # test
    loc_2.LclTranslation.Set(
        fbx.FbxDouble4(2, 0, 0, 0)
    )

    loc_2.LclRotation.Set(
        fbx.FbxDouble4(*euler_aim + [0])
    )

    # test rotation order

    loc_3.SetRotationOrder(
        loc_3.eSourcePivot,
        fbx.eEulerZYX
    )

    loc_3.LclTranslation.Set(
        fbx.FbxDouble4(3, 0, 0, 0)
    )

    loc_3.LclRotation.Set(
        fbx.FbxDouble4(
            *poop_aim + [0]
            #*sp_rot.as_euler('zyx', degrees=True).tolist() + [0]
        )
    )

    loc_1_mat = loc_1.EvaluateGlobalTransform()
    print loc_1_mat.GetR()

    loc_2_mat = loc_2.EvaluateGlobalTransform()
    print loc_2_mat.GetR()

    loc_3_mat = loc_3.EvaluateGlobalTransform()
    print loc_3_mat.GetR()

    return fbx_manager, fbx_scene


def export_scene():
    fbx_manager, fbx_scene = create_scene()

    fbxIO.export_scene(
        fbx_manager,
        fbx_scene,
        EXPORT_FILEPATH,
        settings=None,
        ascii=True
    )

    print "done"


if __name__ == "__main__":
    export_scene()
    #     test = scipy_rotation.from_euler('xyz', [0, 0, 10], degrees=True)
    #     print test.as_dcm()
#     test = scipy_rotation.from_dcm(
#         numpy.array([
#             [0, -1, 0],
#             [1, 0, 0],
#             [0, 0, 1]
#         ])
#     )
    # print test.as_euler('XYZ', degrees=True)

#     print numpy.array([
#         [0, -1, 0],
#         [1, 0, 0],
#         [0, 0, 1]
#     ]).transpose()
