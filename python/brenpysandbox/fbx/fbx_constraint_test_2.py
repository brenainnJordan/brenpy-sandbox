'''
Created on 26 Mar 2019

@author: Bren

Import a scene with constraints, change some stuff and re-export



laaaaaaaaaaaame:

"There is no constraint evaluator in the FBX SDK.
To evaluate the constraints, you must provide your own evaluator,
or use an application that supports them, for example MotionBuilder or Maya."

https://forums.autodesk.com/t5/fbx-forum/applying-constraints-to-effectors/td-p/4014103


'''

import fbx

TEST_FILE = r"C:\Users\Bren\Desktop\tests\maya_constraints_test_002.fbx"
# TEST_FILE = r"C:\Users\Bren\Desktop\tests\constraints_test_001.fbx"
# TEST_FILE = r"C:\Users\Bren\Desktop\tests\constraints_test_002.fbx"

TEST_EXPORT_FILE = r"C:\Users\Bren\Desktop\tests\constraints_test_002.fbx"
TEST_EXPORT_FILE = None

fbx_manager = fbx.FbxManager.Create()
io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
#
# print io_settings.GetBoolProp(fbx.EXP_FBX_ANIMATION, False)
# print io_settings.GetBoolProp(fbx.EXP_FBX_CONSTRAINT, False)

fbx_manager.SetIOSettings(io_settings)
fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")


fbx_importer.Initialize(
    TEST_FILE, -1, fbx_manager.GetIOSettings()
)


fbx_scene = fbx.FbxScene.Create(fbx_manager, "TestScene")
fbx_importer.Import(fbx_scene)
fbx_importer.Destroy()


# find constraints and nodes
p_cons = None

src_count = fbx_scene.GetSrcObjectCount()

for i in range(src_count):
    src = fbx_scene.GetSrcObject(i)
    if isinstance(src, fbx.FbxConstraint):
        p_cons = src
        break


node2 = p_cons.GetConstrainedObject()
node1 = p_cons.GetConstraintSource(0)
node0 = node1.GetParent()

# print cons connections
src_count = p_cons.GetSrcObjectCount()

for i in range(src_count):
    src = p_cons.GetSrcObject(i)
    print "src: {} {}".format(src.GetName(), src)

dst_count = p_cons.GetDstObjectCount()

for i in range(dst_count):
    dst = p_cons.GetDstObject(i)
    print "dst: {} {}".format(dst.GetName(), dst)


# change some stuff
fbx_eval = fbx_scene.GetAnimationEvaluator()
fbx_eval.Reset()
fbx_eval.Flush(node0.LclTranslation)
fbx_eval.Flush(node1.LclTranslation)
fbx_eval.Flush(node2.LclTranslation)

node0.LclTranslation.Set(fbx.FbxDouble3(6, 7, 8))
node1.LclTranslation.Set(fbx.FbxDouble3(10, 11, 12))

fbx_eval.Flush(node0)
fbx_eval.Flush(node1)
fbx_eval.Flush(node2)
fbx_eval.Reset()
# TODO figure out why the constraint is not evaluating!
print list(node0.LclTranslation.Get())
print list(node1.LclTranslation.Get())
print list(node2.LclTranslation.Get())

print fbx_eval.GetNodeLocalTranslation(
    node2,  fbx.FbxTime(0.0), fbx.FbxNode.eSourcePivot, True, True)

if TEST_EXPORT_FILE is not None:
    # FbxCommon.SaveScene(man, scene, TEST_FILE)
    # export
    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    # print io_settings.GetBoolProp(fbx.EXP_FBX_ANIMATION, False)
    # print io_settings.GetBoolProp(fbx.EXP_FBX_CONSTRAINT, False)

    io_settings.SetBoolProp(fbx.EXP_FBX_ANIMATION, True)
    io_settings.SetBoolProp(fbx.EXP_FBX_CONSTRAINT, True)

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
