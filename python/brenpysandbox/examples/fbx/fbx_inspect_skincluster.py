'''
Created on 25 May 2019

@author: Bren

Load fbx file containing skinned geometry and get data such as skin weights.

'''

import os
import fbx
import numpy

SRC_DATA_DIR = r"D:\Repos\dataDump\fbx_tests"

TEST_FILE = r"rig_to_test_001.fbx"


DEFORMER_TYPE_STR = {
    fbx.FbxDeformer.eUnknown: "FbxDeformer.eUnknown",
    fbx.FbxDeformer.eSkin: "FbxDeformer.eSkin",
    fbx.FbxDeformer.eBlendShape: "FbxDeformer.eBlendShape",
}

SUB_DEFORMER_TYPE_STR = {
    fbx.FbxSubDeformer.eUnknown: "FbxSubDeformer.eUnknown",
    fbx.FbxSubDeformer.eCluster: "FbxSubDeformer.eCluster",
    fbx.FbxSubDeformer.eBlendShapeChannel: "FbxSubDeformer.eBlendShapeChannel"
}


SKIN_TYPE_STR = {
    fbx.FbxSkin.eRigid: "FbxSkin.eRigid",
    fbx.FbxSkin.eLinear: "FbxSkin.eLinear",
    fbx.FbxSkin.eDualQuaternion: "FbxSkin.eDualQuaternion",
    fbx.FbxSkin.eBlend: "FbxSkin.eBlend",
}


def find_skin_deformers(fbx_scene):

    skin_deformers = []

    # list all FbxSkin objects in the scene
    skin_count = fbx_scene.GetSrcObjectCount(
        # includes classes that derive from specified class:
        #     fbx.FbxCriteria.ObjectType(fbx.FbxMesh.ClassId)
        # specified class only:
        fbx.FbxCriteria.ObjectTypeStrict(fbx.FbxSkin.ClassId)
    )

    for i in range(skin_count):
        skin_deformer = fbx_scene.GetSrcObject(
            fbx.FbxCriteria.ObjectTypeStrict(fbx.FbxSkin.ClassId),
            i
        )

        skin_deformers.append(skin_deformer)

    return skin_deformers


def inspect_skin_deformer(skin_deformer):

    print "\n *** skin deformer ***\n"

    # ** inherits from fbx.FbxDeformer **

    # fbx does not store maya skin cluster names!
    # but could it?
    # TODO test
    print skin_deformer.GetName()
    skin_deformer.SetName("poop")
    print skin_deformer.GetName()

    print SKIN_TYPE_STR[
        skin_deformer.GetSkinningType()
    ]

    print DEFORMER_TYPE_STR[
        skin_deformer.GetDeformerType()
    ]

    print "Accuracy: {}%".format(
        skin_deformer.GetDeformAccuracy()
    )

    print "Cluster count: ", skin_deformer.GetClusterCount()

    # TODO
    # this might be stored per cluster??
    blend_weights = skin_deformer.GetControlPointBlendWeights()
    print "blend weights: ", blend_weights

    mesh_attr = skin_deformer.GetGeometry()
    print "deformed mesh: ", mesh_attr.GetNode().GetName()
    print "mesh point count: ", mesh_attr.GetControlPointsCount()

    print "\n *** clusters ***\n"

    # ** inherits from fbx.FbxSubDeformer **

#     for i in range(skin_deformer.GetClusterCount()):
    cluster_1 = skin_deformer.GetCluster(1)

    print cluster_1.GetName()

    print SUB_DEFORMER_TYPE_STR[
        cluster_1.GetSubDeformerType()
    ]

    influence_node = cluster_1.GetLink()
    print "influence: ", influence_node.GetName()
    print "point count: ", cluster_1.GetControlPointIndicesCount()
    print "point indices: ", cluster_1.GetControlPointIndices()
    print "weights: ", cluster_1.GetControlPointWeights()

    # weights

    print "\n *** skin weights *** \n"
    influences = get_skin_deformer_influences(skin_deformer)
    inf_names = [i.GetName() for i in influences]
    print "influences: ", inf_names
    weights = get_skin_deformer_weights(skin_deformer, as_numpy=True)
    print "weights: ", weights

    print weights.sum(axis=0)
    print weights.sum(axis=0).sum()


def get_skin_deformer_weights(skin_deformer, as_numpy=True):
    """
    """

    mesh_attr = skin_deformer.GetGeometry()

    point_count = mesh_attr.GetControlPointsCount()
    influence_count = skin_deformer.GetClusterCount()

    skin_weights = numpy.zeros([influence_count, point_count])

    for i in range(
        skin_deformer.GetClusterCount()
    ):
        cluster = skin_deformer.GetCluster(i)
        cluster_weight_indices = cluster.GetControlPointIndices()
        cluster_weights = cluster.GetControlPointWeights()

        skin_weights[i][cluster_weight_indices] = cluster_weights

    if as_numpy:
        return skin_weights
    else:
        return skin_weights.aslist()


def get_skin_deformer_influences(skin_deformer):
    """Get influence for each cluster found in skin deformer.

    returns: list of FbxNodes

    """
    influences = []

    for i in range(
        skin_deformer.GetClusterCount()
    ):
        cluster = skin_deformer.GetCluster(i)
        influence = cluster.GetLink()

        influences.append(influence)

    return influences


def inspect_fbx_file(filepath):

    fbx_manager = fbx.FbxManager.Create()

    io_settings = fbx.FbxIOSettings.Create(fbx_manager, fbx.IOSROOT)
    fbx_manager.SetIOSettings(io_settings)

    fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")

    try:
        fbx_importer.Initialize(
            filepath, -1, fbx_manager.GetIOSettings()
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

    # find skin deformers and do stuff
    skin_deformers = find_skin_deformers(fbx_scene)

    for skin_deformer in skin_deformers:
        inspect_skin_deformer(skin_deformer)

    ### CLEANUP ###
    fbx_manager.Destroy()
    del fbx_manager, fbx_scene

    print "done"


if __name__ == "__main__":
    inspect_fbx_file(
        os.path.join(SRC_DATA_DIR, TEST_FILE)
    )
