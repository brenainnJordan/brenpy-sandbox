'''Example of how to create and export FbxSkeleton nodes.

Created on 10 Mar 2019

@author: Bren

notes:

FbxSkeleton docs:
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_cpp_ref_class_fbx_skeleton_html

'''
import json
import fbx
import FbxCommon

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\joints_export_test_001.fbx"


def print_skeleton_types():
    """Find and print skeleton type enums.
    """
    for i in dir(fbx.FbxSkeleton):
        try:
            cls = getattr(fbx.FbxSkeleton, i)
            if type(cls) == fbx.FbxSkeleton.EType:
                print i, cls, type(cls)
        except AttributeError:
            pass


def create_skel_nodes(fbx_manager):
    """Create a root and some joints.
    """

    # create root
    root_name = "root"
    root_attr = fbx.FbxSkeleton.Create(fbx_manager, root_name)
    root_attr.SetSkeletonType(fbx.FbxSkeleton.eRoot)

    root_node = fbx.FbxNode.Create(fbx_manager, root_name)
    root_node.SetNodeAttribute(root_attr)

    # create joint1
    joint1_name = "joint1"
    joint1_attr = fbx.FbxSkeleton.Create(fbx_manager, joint1_name)
    joint1_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)

    joint1_node = fbx.FbxNode.Create(fbx_manager, joint1_name)
    joint1_node.SetNodeAttribute(joint1_attr)

    joint1_node.LclTranslation.Set(
        fbx.FbxDouble3(50.0, 0.0, 0.0)
    )

    # set prefered angle (both methods work)
    if True:
        prop = joint1_node.FindProperty("PreferedAngleX")
        print prop.IsValid()
        print prop.Set(15.0)
    else:

        joint1_node.SetPreferedAngle(
            # vector4 will accept 3 args
            fbx.FbxVector4(0.0, 0.0, 35.0)
        )

    # *** set joint orientation ****

    # not sure what this does?!
#     joint1_node.SetPivotState(
#         joint1_node.eSourcePivot,
#         joint1_node.ePivotActive
#     )
#
#     joint1_node.SetPivotState(
#         joint1_node.eDestinationPivot,
#         joint1_node.ePivotActive
#     )

    # When this flag is set to false, the RotationOrder,
    # the Pre/Post rotation values and the rotation limits should be ignored.
    # (False by default)
    joint1_node.SetRotationActive(True)

    # suggestion from forum to update pivots (not supported in Python)
    # https://forums.autodesk.com/t5/fbx-forum/manipulating-the-prerotation-property/m-p/4278262
#     joint1_node.UpdatePivotsAndLimitsFromProperties()

    if True:
        # (this method works)
        # Pivot context identifier.
        # eSourcePivot: The source pivot context.
        # eDestinationPivot:The destination pivot context.
        joint1_node.SetPreRotation(
            #         joint1_node.eDestinationPivot, # != joint orientation
            joint1_node.eSourcePivot,  # == joint orientation
            fbx.FbxVector4(0.0, 0.0, 15.0)
        )
    else:
        # (this method does not work)
        # TODO find out why
        # set joint orientation ????
        jo_prop = joint1_node.FindProperty("PreRotation")
    #     jo_cast_prop = fbx.FbxPropertyDouble3(jo_prop)
    #     print help(jo_cast_prop)
    #     jo_cast_prop[2].Set(15.0)
        print jo_prop.Set(
            fbx.FbxDouble3(0.0, 0.0, 15.0)
        )

    # create joint2
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

    # add some custom data
    test_prop = fbx.FbxProperty.Create(
        joint2_node, fbx.FbxStringDT, "testStringProperty"
    )

    test_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)

    print test_prop.Set(fbx.FbxString("some stuff about things"))

    # dict test
    # TODO test deserializing this
    test_prop = fbx.FbxProperty.Create(
        joint2_node, fbx.FbxStringDT, "testDictProperty"
    )

    test_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)

    # animatable double
    print test_prop.Set(
        fbx.FbxString(
            json.dumps({"test": 1.0, "things": "blah", "stuff": True})
        )
    )

    test_dbl_prop = fbx.FbxProperty.Create(
        joint2_node, fbx.FbxDoubleDT, "testDoubleProperty"
    )

    test_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    test_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    print test_dbl_prop.Set(16.0)

    # note: float property gets converted into double
    # after importing into Maya and exporting out again
    test_float_prop = fbx.FbxProperty.Create(
        joint2_node, fbx.FbxFloatDT, "testFloatProperty"
    )

    test_float_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)

#     cast_test_prop =
    print test_float_prop.Set(18.0)

    test_dbl3_prop = fbx.FbxProperty.Create(
        joint2_node, fbx.FbxDouble3DT, "testDouble3Property"
    )

    test_dbl3_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    test_dbl3_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    print test_dbl3_prop.Set(
        1.3
        #         [1.1, 2.2, 3.3]
        #         fbx.FbxDouble3(1.1, 2.2, 3.3)
    )

    # create joint3
    joint3_name = "joint3"
    joint3_attr = fbx.FbxSkeleton.Create(fbx_manager, joint3_name)
    joint3_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)
    # if we wanted to use IK:
    # joint3_attr.SetSkeletonType(fbx.FbxSkeleton.eEffector)

    joint3_node = fbx.FbxNode.Create(fbx_manager, joint3_name)
    joint3_node.SetNodeAttribute(joint3_attr)

    joint3_node.LclTranslation.Set(
        fbx.FbxDouble3(20.0, 0.0, 0.0)
    )

    # Build skeleton node hierarchy
    root_node.AddChild(joint1_node)
    joint1_node.AddChild(joint2_node)
    joint2_node.AddChild(joint3_node)

    return root_node


def export_skel():
    """Create a manager, scene, skel and export file.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")
    root_node = create_skel_nodes(fbx_manager)

    fbx_scene.GetRootNode().AddChild(root_node)

    if False:
        # save file using FbxCommon
        res = FbxCommon.SaveScene(fbx_manager, fbx_scene, TEST_EXPORT_FILE)
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
    #     print_skeleton_types()
    export_skel()

    print "done"
