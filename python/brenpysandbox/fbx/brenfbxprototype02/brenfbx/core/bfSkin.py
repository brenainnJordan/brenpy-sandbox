'''
Created on 26 May 2019

@author: Bren

openmaya docs:
http://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__py_ref_index_html

'''

import fbx
import numpy


def find_skin_deformers(fbx_scene):
    """List all FbxSkin deformers in the scene
    """
    skin_deformers = []

    skin_count = fbx_scene.GetSrcObjectCount(
        fbx.FbxCriteria.ObjectTypeStrict(fbx.FbxSkin.ClassId)
    )

    for i in range(skin_count):
        skin_deformer = fbx_scene.GetSrcObject(
            fbx.FbxCriteria.ObjectTypeStrict(fbx.FbxSkin.ClassId),
            i
        )

        skin_deformers.append(skin_deformer)

    return skin_deformers


def find_skin_deformer_for_mesh(mesh_attr, fbx_scene):
    """Search the scene for a skin deformer that affects specified mesh attribute.
    """
    for skin_deformer in find_skin_deformers(fbx_scene):
        i_mesh_attr = skin_deformer.GetGeometry()
        if i_mesh_attr is mesh_attr:
            return skin_deformer

    return None


def get_skin_deformer_weights(skin_deformer, as_numpy=True):
    """Return a list of weights for all influences and all points.
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
        return skin_weights.tolist()


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
