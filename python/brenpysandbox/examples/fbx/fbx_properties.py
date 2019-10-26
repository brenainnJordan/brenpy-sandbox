'''
Created on 9 Mar 2019

@author: Bren

notes:

docs:
http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_cpp_ref_annotated_html


Property casting:

https://forums.autodesk.com/t5/fbx-forum/fbxproperty-get-in-2013-1-python/td-p/4243290

"As of FBX 2013.1... We do not support user-created properties yet in the Python SDK."



'''

import fbx


# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_fbx_ascii_test_001.fbx"
# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_export_test_001.fbx"
# TEST_FILE = r"C:\Users\Bren\Desktop\tests\test_blah2.fbx"
# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_aim_test_001.fbx"
TEST_FILE = r"C:\Users\Bren\Desktop\tests\maya_constraints_test_002.fbx"


def get_fbx_enums():
    for i in dir(fbx):
        if i.startswith("e"):
            print i


def get_fbx_properties():
    for i in dir(fbx):
        if i.startswith("FbxProperty"):
            print i


FBX_PROPERTY_TYPES = {
    fbx.EFbxRotationOrder: {
        fbx.eEulerXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
        fbx.eEulerXZY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
        fbx.eEulerYXZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
        fbx.eEulerYZX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
        fbx.eEulerZXY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
        fbx.eEulerZYX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
        fbx.eSphericXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?????
    },
    fbx.EFbxType: {
        fbx.eFbxBlob: fbx.FbxPropertyBlob,
        fbx.eFbxBool: fbx.FbxPropertyBool1,
        #     fbx.eFbxChar
        fbx.eFbxDateTime: fbx.FbxPropertyDateTime,
        #     fbx.eFbxDistance
        fbx.eFbxDouble: fbx.FbxPropertyDouble1,
        fbx.eFbxDouble2: fbx.FbxPropertyDouble2,
        fbx.eFbxDouble3: fbx.FbxPropertyDouble3,
        fbx.eFbxDouble4: fbx.FbxPropertyDouble4,
        #     fbx.eFbxDouble4x4 ??? fbx.FbxPropertyXMatrix
        fbx.eFbxEnum: fbx.FbxPropertyEnum,
        fbx.eFbxFloat: fbx.FbxPropertyFloat1,
        #     fbx.eFbxHalfFloat
        fbx.eFbxInt: fbx.FbxPropertyInteger1,
        fbx.eFbxLongLong: fbx.FbxPropertyInteger1,  # MAYBE ??????
        fbx.eFbxReference: fbx.FbxPropertyFbxReference,
        fbx.eFbxShort: fbx.FbxPropertyInteger1,  # MAYBE ??????
        fbx.eFbxString: fbx.FbxPropertyString,
        fbx.eFbxTime: fbx.FbxPropertyFbxTime,
        #     fbx.eFbxTypeCount
        fbx.eFbxUChar: fbx.FbxPropertyString,
        fbx.eFbxUInt: fbx.FbxPropertyInteger1,  # MAYBE ??????
        fbx.eFbxULongLong: fbx.FbxPropertyInteger1,  # MAYBE ??????
        fbx.eFbxUShort: fbx.FbxPropertyInteger1,  # MAYBE ??????
        #     fbx.eFbxUndefined
    },
    fbx.EFbxQuatInterpMode: {
        fbx.eQuatInterpCount: fbx.FbxPropertyEFbxQuatInterpMode,  # MAYBE ?????
        fbx.eQuatInterpCubic: fbx.FbxPropertyEFbxQuatInterpMode,  # MAYBE ?????
        fbx.eQuatInterpOff: fbx.FbxPropertyEFbxQuatInterpMode,  # MAYBE ?????
        fbx.eQuatInterpSlerp: fbx.FbxPropertyEFbxQuatInterpMode,  # MAYBE ?????
        fbx.eQuatInterpTangentDependent: fbx.FbxPropertyEFbxQuatInterpMode,  # MAYBE ?????
    }
}

FBX_ENUM_NAMES = {
    fbx.EFbxRotationOrder: {
        fbx.eEulerXYZ: "eEulerXYZ",
        fbx.eEulerXZY: "eEulerXZY",
        fbx.eEulerYXZ: "eEulerYXZ",
        fbx.eEulerYZX: "eEulerYZX",
        fbx.eEulerZXY: "eEulerZXY",
        fbx.eEulerZYX: "eEulerZYX",
        fbx.eSphericXYZ: "eSphericXYZ",
    },
    fbx.EFbxType: {
        fbx.eFbxBlob: "eFbxBlob",
        fbx.eFbxBool: "eFbxBool",
        fbx.eFbxChar: "eFbxChar",
        fbx.eFbxDateTime: "eFbxDateTime",
        fbx.eFbxDistance: "eFbxDistance",
        fbx.eFbxDouble: "eFbxDouble",
        fbx.eFbxDouble2: "eFbxDouble2",
        fbx.eFbxDouble3: "eFbxDouble3",
        fbx.eFbxDouble4: "eFbxDouble4",
        fbx.eFbxDouble4x4: "eFbxDouble4x4",
        fbx.eFbxEnum: "eFbxEnum",
        fbx.eFbxFloat: "eFbxFloat",
        fbx.eFbxHalfFloat: "eFbxHalfFloat",
        fbx.eFbxInt: "eFbxInt",
        fbx.eFbxLongLong: "eFbxLongLong",
        fbx.eFbxReference: "eFbxReference",
        fbx.eFbxShort: "eFbxShort",
        fbx.eFbxString: "eFbxString",
        fbx.eFbxTime: "eFbxTime",
        fbx.eFbxTypeCount: "eFbxTypeCount",
        fbx.eFbxUChar: "eFbxUChar",
        fbx.eFbxUInt: "eFbxUInt",
        fbx.eFbxULongLong: "eFbxULongLong",
        fbx.eFbxUShort: "eFbxUShort",
        fbx.eFbxUndefined: "eFbxUndefined",
    },
    fbx.EFbxQuatInterpMode: {
        fbx.eQuatInterpClassic: "eQuatInterpClassic",
        fbx.eQuatInterpCount: "eQuatInterpCount",
        fbx.eQuatInterpCubic: "eQuatInterpCubic",
        fbx.eQuatInterpOff: "eQuatInterpOff",
        fbx.eQuatInterpSlerp: "eQuatInterpSlerp",
        fbx.eQuatInterpTangentDependent: "eQuatInterpTangentDependent",
    }
}


def print_object_properties(fbx_object):

    # print object name
    node_name = fbx_object.GetName()
    print node_name, ":"

    # print root property
    root_prop = fbx_object.GetClassRootProperty()
    prop_type_enum = root_prop.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)
    prop_enum_names = FBX_ENUM_NAMES[prop_type]

    print "\trootProperty {}".format(
        prop_enum_names[prop_type_enum]
        # , root_prop.Get()
    )

    # print properties
    prop = fbx_object.GetFirstProperty()

    while prop.IsValid():

        # to get the value of a property,
        # first it must be cast to the appropriate property class
        # the Get() method is not present in the FbxProperty base class.
        # https://forums.autodesk.com/t5/fbx-forum/fbxproperty-get-in-2013-1-python/td-p/4243290
        prop_type_enum = prop.GetPropertyDataType().GetType()
        prop_type = type(prop_type_enum)

        if prop_type in FBX_PROPERTY_TYPES:
            prop_type_enums = FBX_PROPERTY_TYPES[prop_type]
            prop_enum_names = FBX_ENUM_NAMES[prop_type]

            if prop_type_enum in prop_type_enums:
                prop_class = prop_type_enums[prop_type_enum]

                # cast property
                cast_prop = prop_class(prop)

                # print data
                print "\tprop {0} {1} ({2}) {3} {4}".format(
                    cast_prop.GetName(),
                    prop_enum_names[prop_type_enum],
                    cast_prop.Get(),
                    prop_type_enum.__class__.__name__,
                    prop.GetParent().IsRoot()
                )

            elif prop_type_enum in prop_enum_names:
                print "Property type not supported: {0} {1}".format(
                    prop.GetName(), prop_enum_names[prop_type_enum]
                )
            else:
                print "Property type enum not supported: {0}".format(
                    prop.GetName()
                )
        else:
            print "Property type not supported: {0}".format(
                prop_type
            )

        prop = fbx_object.GetNextProperty(prop)

    print "\n"

    if isinstance(fbx_object, fbx.FbxNode):
        # Recursively print the children.
        for i in range(fbx_object.GetChildCount()):
            print_object_properties(fbx_object.GetChild(i))


def inspect_fbx_file_node_properties(file_path):

    fbx_manager = fbx.FbxManager.Create()
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    fbx_manager.SetIOSettings(io_settings)
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

    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")
    fbx_importer.Import(fbx_scene)
    fbx_importer.Destroy()
    fbx_root_node = fbx_scene.GetRootNode()

    if False:
        # only print node properties
        print "*** NODE PROPERTIES ***"
        if fbx_root_node:
            for i in range(fbx_root_node.GetChildCount()):
                # print fbx_root_node.GetChild(i)
                print_object_properties(fbx_root_node.GetChild(i))
    else:
        # print all objects
        print "*** OBJECT PROPERTIES ***"
        src_count = fbx_scene.GetSrcObjectCount()

        for i in range(src_count):
            src = fbx_scene.GetSrcObject(i)
            print_object_properties(src)

    # cleanup
    fbx_manager.Destroy()
    del fbx_manager, fbx_scene

    print "done"


if __name__ == "__main__":
    inspect_fbx_file_node_properties(TEST_FILE)
#     get_fbx_enums()
