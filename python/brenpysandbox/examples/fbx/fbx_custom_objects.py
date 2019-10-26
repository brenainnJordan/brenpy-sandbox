'''
Created on 27 Apr 2019

@author: Bren

Test creating a "custom" FbxObject, add properties, export file and read back.

"Custom" FbxObject classes are not actually possible in fbx python.

Instead we can use a regular FbxObject, and wrap inside a python class that enforces expected behaviour.
We would only interact with the FbxObject via the python class.

http://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_cpp_ref_class_fbx_object_html

subclassing FbxObject is only possible in C++

So in order to describe a rig building system, it may be neccesary
to use a hierarchy of named objects with properties and connections,
similar to a node graph.

When it comes to reading a file with these objects,
we would need to first find these objects by name via connections,
then instance a custom class that points to the object,
and provides a function set with the expected behaviour.

'''

import fbx
import FbxCommon
import json
from brenpy.examples.fbx.fbx_constraints import fbx_manager

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\fbx_object_test1.fbx"


class FbxFnTestObject(object):
    """Test function set class.

    Similar to OpenMaya "Fn" classes.

    Instances of this class do not live in the fbx scene, but simply points to an object
    in the scene that we expect to follow certain rules, such as
    having specific user properties, with specific types.

    This would represent our "custom" FbxObject type.

    TODO add a property that describes this class.

    In many ways this is similar to deserializing a json file, to a dictionary,
    then to a python class instance.

    Except in this case, the data source is not a json file, but an FbxObject,
    and we do not deserialize data, rather we create references
    to the source of the data (eg an FbxProperty instance).

    The advantage of this is we can still leverage the features of fbx classes,
    while enforcing additional rules and/or adding additional features for our "custom type".

    """

    def __init__(self, fbx_object):
        self._object = fbx_object

        self.test_dbl_prop = fbx.FbxProperty()

        self._initialize_properties()

    @property
    def object(self):
        """Return internal fbx.FbxObject.
        """
        return self._object

    def _initialize_properties(self):
        """Look for expected test property and create if it doesn't exist.
        """
        case_sensitive = True

        test_dbl_prop = self.object.FindProperty(
            "testDoubleProperty", case_sensitive
        )

        # check property is expected type
        if test_dbl_prop.IsValid():
            # TODO make enums readable in error message

            if test_dbl_prop.GetPropertyDataType().GetType() != fbx.eFbxDouble:
                raise Exception(
                    "Property type ({}) does not match expected type ({})".format(
                        test_dbl_prop.GetPropertyDataType().GetType(),
                        fbx.eFbxDouble
                    )
                )

        else:
            # if property does not exist, create property with default value

            test_dbl_prop = fbx.FbxProperty.Create(
                self.object, fbx.FbxDoubleDT, "testDoubleProperty"
            )

            test_dbl_prop.ModifyFlag(
                fbx.FbxPropertyFlags.eUserDefined, True)
            test_dbl_prop.ModifyFlag(
                fbx.FbxPropertyFlags.eAnimatable, True)

            test_dbl_prop.Set(16.0)

        self.test_dbl_prop = fbx.FbxPropertyDouble1(
            test_dbl_prop
        )

    def IsValid(self):
        # check properties are all valid
        return all(
            self.test_dbl_prop.IsValid()
        )

    @staticmethod
    def Create(*args, **kwargs):
        fbx_object = fbx.FbxObject.Create(*args, **kwargs)

        return FbxFnTestObject(fbx_object)


def create_objects(fbx_manager, fbx_scene):
    """Create two FbxObjects and add to the scene.
    The first object is a "non custom" object.
    The second object is our "custom" object. 
    """

    # create "non custom" object
    test_object = fbx.FbxObject.Create(fbx_manager, "test_object_blah")
    fbx_scene.ConnectSrcObject(test_object)

    # add some custom data
    test_prop = fbx.FbxProperty.Create(
        test_object, fbx.FbxStringDT, "testStringProperty"
    )

    test_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    test_prop.Set(fbx.FbxString("some stuff about things"))

    # dict test
    test_prop = fbx.FbxProperty.Create(
        test_object, fbx.FbxStringDT, "testDictProperty"
    )

    test_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)

    # animatable double
    test_prop.Set(
        fbx.FbxString(
            json.dumps({"test": 1.0, "things": "blah", "stuff": True})
        )
    )

    test_dbl_prop = fbx.FbxProperty.Create(
        test_object, fbx.FbxDoubleDT, "testDoubleProperty"
    )

    test_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
    test_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

    test_dbl_prop.Set(16.0)

    # test custom object

#     # This does not work...
#     fbx_manager.RegisterFbxClass(
#         "MyClassName",
#         #         fbx.FBX_TYPE(FbxTestObject),
#         #         fbx.FBX_TYPE(fbx.FbxObject)
#     )

    test_custom_fn = FbxFnTestObject.Create(fbx_manager, "CustomStuff")
    # note to add the object to the scene we need to access the object
    # via the .object property
    fbx_scene.ConnectSrcObject(test_custom_fn.object)

    # modify property value via function set
    test_custom_fn.test_dbl_prop.Set(13.3)


def export_objects():
    """Create a manager, scene, skel, objects and export file.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    create_objects(fbx_manager, fbx_scene)

    if True:
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

    print "export done"


def deserialize_objects(fbx_scene):
    """Find custom object and wrap with custom function set class.
    """
    custom_object = fbx_scene.FindSrcObject("CustomStuff", 0)
    test_null = fbx_scene.FindSrcObject("something_that_does_not_exist", 0)

    print "imported custom object: ", custom_object  # fbx.FbxObject instance
    print "imported null object: ", test_null  # None

    custom_object_fn = FbxFnTestObject(custom_object)

    print custom_object_fn.test_dbl_prop.Get()


def import_objects():
    """Import fbx file and find objects.
    """
    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

    # create importer objects
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    fbx_manager.SetIOSettings(io_settings)
    fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")

    # Use the first argument as the filename for the importer.
    try:
        fbx_importer.Initialize(
            TEST_EXPORT_FILE, -1, fbx_manager.GetIOSettings()
        )
    except Exception as err:
        msg = "Call to FbxImporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            fbx_importer.GetStatus().GetErrorString()
        )
        print msg
        raise err

    # import file into scene
    fbx_importer.Import(fbx_scene)
    fbx_importer.Destroy()

    # get nodes
    deserialize_objects(fbx_scene)

    # cleanup
    fbx_manager.Destroy()
    del fbx_manager, fbx_scene

    print "import done"


if __name__ == "__main__":
    export_objects()
    import_objects()

    print "done"
