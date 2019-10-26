'''
Created on 28 Apr 2019

@author: Bren
'''

import fbx

# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_fbx_ascii_test_001.fbx"
TEST_FILE = r"C:\Users\Bren\Desktop\tests\maya_constraints_test_001.fbx"


def print_constraint_references(fbx_scene):
    cons = fbx_scene.FindSrcObject("node2_parentConstraint1", 0)

    if not cons:
        raise Exception("node2_parentConstraint1 not found")

    case_sensitive = False

    constraint_property = cons.FindProperty(
        "Constrained object (Child)", case_sensitive
    )

    if not constraint_property.IsValid():
        raise Exception(
            "Could not find property: 'Constrained object (Child)'")

    constrained_node = constraint_property.GetSrcObject(0)
    print "referenced node: ", constrained_node.GetName()

    # we can also cast this property and get the value
    # the value being a FbxReference instance
    # but what can we do with this??
    # TODO find out
    cast_prop = fbx.FbxPropertyFbxReference(constraint_property)
    ref = cast_prop.Get()  # FbxReference
    print ref


def inspect_fbx_file(file_path):
    """Import (load) fbx file into memory and print some stuff about it.
    """

    fbx_manager = fbx.FbxManager.Create()
    fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")

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

    # Create a new scene so that it can be populated by the imported file.
    fbx_importer.Import(fbx_scene)
    fbx_importer.Destroy()

    print_constraint_references(fbx_scene)

    ### CLEANUP ###
    fbx_manager.Destroy()
    del fbx_manager, fbx_scene

    print "done"


if __name__ == "__main__":
    inspect_fbx_file(TEST_FILE)
