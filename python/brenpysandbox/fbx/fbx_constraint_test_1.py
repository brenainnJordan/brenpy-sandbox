'''
Created on 26 Mar 2019

@author: Bren
'''

TEST_FILE = r"C:\Users\Bren\Desktop\tests\constraints_test_003.fbx"

import fbx
import FbxCommon

from bfbx.bfbxcore import fbxIO
reload(fbxIO)

fbx_manager = fbx.FbxManager()
scene = fbx.FbxScene.Create(fbx_manager, "testscene")

root = scene.GetRootNode()

node0 = fbx.FbxNode.Create(fbx_manager, "node0")
node1 = fbx.FbxNode.Create(fbx_manager, "node1")
node2 = fbx.FbxNode.Create(fbx_manager, "node2")

root.AddChild(node0)
node0.AddChild(node1)
root.AddChild(node2)

# to export constraints we need an anim stack
lAnimStack = fbx.FbxAnimStack.Create(scene, "testAnimStack")
lAnimLayer = fbx.FbxAnimLayer.Create(scene, "Base Layer")
lAnimStack.AddMember(lAnimLayer)

# create constraint
p_cons = fbx.FbxConstraintParent.Create(fbx_manager, "node2_parentConstraint")
scene.ConnectSrcObject(p_cons)

# a source is necessary to import without errors
weight = 100
p_cons.AddConstraintSource(node1, weight)
p_cons.SetConstrainedObject(node2)

print p_cons.AffectTranslationX.Get()

# node1.ConnectDstObject(p_cons)

# p_cons.ConnectDstObject(scene)
#
# node2.ConnectDstObject(p_cons)
node1.ConnectDstObject(p_cons)
node1.LclTranslation.ConnectDstObject(p_cons)
node0.LclTranslation.ConnectDstObject(p_cons)

node2.ConnectSrcObject(p_cons)
node2.LclTranslation.ConnectSrcObject(p_cons)

node2.ConnectSrcObject(lAnimStack)
p_cons.ConnectDstObject(lAnimStack)
p_cons.ConnectSrcObject(lAnimStack)

# TODO try animating node0/1 ?????

fbx_eval = scene.GetAnimationEvaluator()
fbx_eval.Reset()

print p_cons.ConstrainedObject
print p_cons.ConstraintSources
# print p_cons.GetConstraintSource(0).GetName()
print p_cons.GetConstrainedObject().GetName()

fbx_eval.Flush(node0.LclTranslation)
fbx_eval.Flush(node1.LclTranslation)
fbx_eval.Flush(node2.LclTranslation)

node0.LclTranslation.Set(fbx.FbxDouble3(6, 7, 8))
node1.LclTranslation.Set(fbx.FbxDouble3(10, 11, 12))

fbx_eval.Flush(node0.LclTranslation)
fbx_eval.Flush(node1.LclTranslation)
fbx_eval.Flush(node2.LclTranslation)

# TODO figure out why the constraint is not evaluating!
print list(node1.LclTranslation.Get())
print list(node2.LclTranslation.Get())
print p_cons.Active.Get()

fbx_eval.Reset()

fbx_eval.GetNodeGlobalTransform(node1).GetT()
world_matrix = fbx_eval.GetNodeGlobalTransform(node2)
print world_matrix.GetT()


fbx_eval = scene.GetAnimationEvaluator()
# fbx_eval = fbx.FbxAnimEvaluator.Create(fbx_manager, "blah")

fbx_eval.Flush(node0.LclTranslation)
fbx_eval.Flush(node1.LclTranslation)
fbx_eval.Flush(node2.LclTranslation)

# fbx_eval.Reset()


node0.LclTranslation.Set(fbx.FbxDouble3(6, 7, 8))
node1.LclTranslation.Set(fbx.FbxDouble3(10, 11, 12))

fbx_eval.Reset()

time_zero = fbx.FbxTime()
time_zero.SetSecondDouble(1.0)
print fbx_eval.ValidateTime(time_zero).GetSecondDouble()

mat = fbx_eval.GetNodeGlobalTransform(node2, time_zero)
print mat.GetT()

print fbx_eval.GetNodeLocalTransform(node2, time_zero).GetT()

# print fbx_eval.GetPropertyValue(node2.LclTranslation, time_zero).Get(
#     fbx.eFbxDouble3
# )
fbx_eval.Reset()

if False:
    FbxCommon.SaveScene(fbx_manager, scene, TEST_FILE)
elif False:
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
else:
    # use custom exporter method
    settings = fbxIO.BasicIOSettings()
    settings.constraints = True

#     settings = settings.Create(fbx_manager, fbx.IOSROOT)
#     print settings.GetBoolProp(fbx.EXP_FBX_CONSTRAINT, False)

    # interesting to note that when constraints = False
    # constraint objects are not exported
    # however the constraint connections remain!

    fbxIO.export_scene(
        fbx_manager,
        scene,
        TEST_FILE,
        settings=settings,
        ascii=True
    )
