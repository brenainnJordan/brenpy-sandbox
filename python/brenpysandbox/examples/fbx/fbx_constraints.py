'''Create some nodes and a constraint, then export.

Created on 26 Mar 2019

@author: Bren


Note:

"There is no constraint evaluator in the FBX SDK.
To evaluate the constraints, you must provide your own evaluator,
or use an application that supports them, for example MotionBuilder or Maya."

https://forums.autodesk.com/t5/fbx-forum/applying-constraints-to-effectors/td-p/4014103

(
    super lame :(
)


'''

TEST_FILE = r"C:\Users\Bren\Desktop\tests\constraints_test_001.fbx"

import fbx
import FbxCommon

# create a scene
fbx_manager = fbx.FbxManager()
scene = fbx.FbxScene.Create(fbx_manager, "testscene")

root = scene.GetRootNode()

# create some nulls
node0 = fbx.FbxNode.Create(fbx_manager, "node0")
node1 = fbx.FbxNode.Create(fbx_manager, "node1")
node2 = fbx.FbxNode.Create(fbx_manager, "node2")

root.AddChild(node0)
node0.AddChild(node1)
root.AddChild(node2)

# in order to export constraints we need an anim stack
lAnimStack = fbx.FbxAnimStack.Create(scene, "testAnimStack")
lAnimLayer = fbx.FbxAnimLayer.Create(scene, "Base Layer")
lAnimStack.AddMember(lAnimLayer)

# create constraint
p_cons = fbx.FbxConstraintParent.Create(fbx_manager, "node2_parentConstraint")

# add to scene
scene.ConnectSrcObject(p_cons)

# a source is necessary to import without errors
weight = 100
p_cons.AddConstraintSource(node1, weight)
p_cons.SetConstrainedObject(node2)

# debug
print p_cons.ConstrainedObject
print p_cons.ConstraintSources
print p_cons.GetConstraintSource(0).GetName()
print p_cons.GetConstrainedObject().GetName()

# move target nodes
node0.LclTranslation.Set(fbx.FbxDouble3(6, 7, 8))
node1.LclTranslation.Set(fbx.FbxDouble3(10, 11, 12))

# IMPORTANT
# note that the constraint is not evaluated
print list(node0.LclTranslation.Get())
print list(node1.LclTranslation.Get())
print list(node2.LclTranslation.Get())

# export file
# note that when loading into maya the constraint is not initially evaluated
# cmds.dgdirty(a=True) or cmds.dgdirty("node2") will force the constraint
# to be evaluated

if False:
    FbxCommon.SaveScene(fbx_manager, scene, TEST_FILE)
else:
    # export
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    print io_settings.GetBoolProp(fbx.EXP_FBX_ANIMATION, False)
    print io_settings.GetBoolProp(fbx.EXP_FBX_CONSTRAINT, False)

    io_settings.SetBoolProp(fbx.EXP_FBX_ANIMATION, True)
    io_settings.SetBoolProp(fbx.EXP_FBX_CONSTRAINT, True)

    fbx_manager.SetIOSettings(io_settings)

    exporter = fbx.FbxExporter.Create(fbx_manager, "")

    try:
        exporter.Initialize(
            TEST_FILE, -1, fbx_manager.GetIOSettings()
        )
    except Exception as err:
        msg = "Call to FbxExporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            exporter.GetStatus().GetErrorString()
        )
        print msg
        raise err

    exporter.Export(scene)
    exporter.Destroy()
