'''
Created on 8 Sep 2019

@author: Bren

Notes:
<class 'fbx.FbxAnimCurve'>
<class 'fbx.FbxAnimCurveBase'>
<class 'fbx.FbxAnimCurveNode'>
<class 'fbx.FbxAnimEvaluator'>
<class 'fbx.FbxAnimLayer'>
<class 'fbx.FbxAnimStack'>
<class 'fbx.FbxAudio'>
<class 'fbx.FbxAudioLayer'>
<class 'fbx.FbxBindingOperator'> # shader stuff?
<class 'fbx.FbxBindingTable'> # shader stuff?
<class 'fbx.FbxBindingTableBase'>
<class 'fbx.FbxBlendShape'>
<class 'fbx.FbxBlendShapeChannel'>
<class 'fbx.FbxBoundary'>
<class 'fbx.FbxCache'> # point cache stuff, supports alembic!
<class 'fbx.FbxCamera'>
<class 'fbx.FbxCameraStereo'>
<class 'fbx.FbxCameraSwitcher'>
<class 'fbx.FbxCharacter'>
<class 'fbx.FbxCharacterPose'>
<class 'fbx.FbxCluster'>
<class 'fbx.FbxCollection'> # base of FbxDocument # can share FbxObjects, cannot save with another scene
<class 'fbx.FbxCollectionExclusive'> # can NOT share FbxObjects, CAN save within a scene
<class 'fbx.FbxConstraint'> # possible use case for brenrig (replace modifier class)
<class 'fbx.FbxConstraintAim'>
<class 'fbx.FbxConstraintParent'>
<class 'fbx.FbxConstraintPosition'>
<class 'fbx.FbxConstraintRotation'>
<class 'fbx.FbxConstraintScale'>
<class 'fbx.FbxConstraintSingleChainIK'>
<class 'fbx.FbxControlSetPlug'> # access to ControlSet aka ControlRig!
<class 'fbx.FbxDeformer'> # base class for deformers, not useful by itself?
<class 'fbx.FbxDisplayLayer'> # subclass of FbxCollectionExclusive, can save in scene
<class 'fbx.FbxDocument'>  # base of FbxScene
<class 'fbx.FbxDocumentInfo'> # contains info on saved .fbx file
<class 'fbx.FbxExporter'>
<class 'fbx.FbxFileTexture'>
<class 'fbx.FbxGeometry'>
<class 'fbx.FbxGeometryBase'>
<class 'fbx.FbxGeometryWeightedMap'>
<class 'fbx.FbxGlobalSettings'>
<class 'fbx.FbxIOBase'>
<class 'fbx.FbxIOSettings'>
<class 'fbx.FbxImplementation'> # This object represents the shading node implementation.
<class 'fbx.FbxImporter'>
<class 'fbx.FbxLODGroup'>
<class 'fbx.FbxLayerContainer'> # mesh layer info?
<class 'fbx.FbxLayeredTexture'>
<class 'fbx.FbxLight'>
<class 'fbx.FbxLine'> # basically a linear curve
<class 'fbx.FbxMarker'>
<class 'fbx.FbxMediaClip'>
<class 'fbx.FbxMesh'>
<class 'fbx.FbxNode'>
<class 'fbx.FbxNodeAttribute'> # attaches to node
<class 'fbx.FbxNull'>
<class 'fbx.FbxNurbs'>
<class 'fbx.FbxNurbsCurve'>
<class 'fbx.FbxNurbsSurface'>
<class 'fbx.FbxObject'>
<class 'fbx.FbxPatch'>
<class 'fbx.FbxPose'> # this will be very useful!! (although stores pose as matrix, good or bad?)
<class 'fbx.FbxProceduralTexture'>
<class 'fbx.FbxScene'>
<class 'fbx.FbxSceneReference'> # Contains information about a referenced file. 
<class 'fbx.FbxSelectionNode'> # used with FbxSelectionSet for vertices etc.
<class 'fbx.FbxSelectionSet'> # inherits FbxCollection, but DOES save in scene, useful!
<class 'fbx.FbxShape'> # blendshape stuff, useful!
<class 'fbx.FbxSkeleton'>
<class 'fbx.FbxSkin'>
<class 'fbx.FbxSubDeformer'>
<class 'fbx.FbxSurfaceLambert'>
<class 'fbx.FbxSurfaceMaterial'>
<class 'fbx.FbxSurfacePhong'>
<class 'fbx.FbxTexture'>
<class 'fbx.FbxThumbnail'>
<class 'fbx.FbxTrimNurbsSurface'>
<class 'fbx.FbxVertexCacheDeformer'>
<class 'fbx.FbxVideo'>


'''

import fbx
from inspect import isclass


def list_object_subclasses():
    """List all subclasses of FbxObject that are available in python SDK
    """
    for i in dir(fbx):
        obj = getattr(fbx, i)

        if not isclass(obj):
            continue

        if not issubclass(obj, fbx.FbxObject):
            continue

        print obj


if __name__ == "__main__":
    list_object_subclasses()
