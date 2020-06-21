"""
Stuff
"""

import fbx
import inspect

try:
    import Qt
except ImportError:
    import PySide2 as Qt

# Qt.QtCore.SIGNAL doesn't seem to exist
# TODO investigate why
try:
    from PySide.QtCore import SIGNAL
except ImportError:
    from PySide2.QtCore import SIGNAL

from brenfbx.core import bfCore

ICONS_8_RESOURCES = {
    "square": ":/icons8-square-50.png",
    "3d_touch": "icons8-3d-touch-50",
    "circle": ":/icons8-circle-50.png",
    "filled_circle": ":/icons8-filled-circle-50.png",
    "coordinate_system": ":/icons8-coordinate-system-50.png",
    "coordinate_system_2": ":/icons8-coordinate-system-50-2.png",
    "animated_skeleton": ":/icons8-animated-skeleton-50.png",
    "animated_skeleton_2": ":/icons8-animated-skeleton-50-2.png",
    "dog_bone_50": ":/icons8-dog-bone-50.png",
    "dog_bone_50_2": ":/icons8-dog-bone-50-2.png",
}

RESOURCES = {
    #     "Camera": ":/out_camera.png",
    "FbxNode": ICONS_8_RESOURCES["coordinate_system"],
    "FbxNull": ICONS_8_RESOURCES["coordinate_system_2"],
    "FbxSkeleton": ICONS_8_RESOURCES["dog_bone_50"],
    #     "FbxObject": ":/out_joint.png",
    "DEFAULT": ICONS_8_RESOURCES["circle"]
}


def get_fbx_object_pixmap(fbx_object, scale=None, scale_via_icon=True):
    """TODO use brType property to get name key

    Note:
        scaling via QIcon seems to give nicer results than QPixmap.scaled()

    """
    #     type_name = brutils.get_br_type_name(
    #         fbx_object, err=False, verbose=False
    #     )

    if isinstance(fbx_object, fbx.FbxClassId):
        type_name = fbx_object.GetName()

    elif isinstance(fbx_object, fbx.FbxObject):
        type_name = fbx_object.ClassId.GetName()

    elif inspect.isclass(fbx_object):
        type_name = fbx_object.__name__

    else:
        raise bfCore.BfError(
            "Object not recognised: {}".format(fbx_object)
        )

    if type_name in RESOURCES.keys():
        resource = RESOURCES[type_name]
    else:
        resource = RESOURCES["DEFAULT"]

    pixmap = Qt.QtGui.QPixmap(resource)

    if scale is not None:
        if scale_via_icon:
            icon = Qt.QtGui.QIcon(
                pixmap
            )
            pixmap = icon.pixmap(*scale)
        else:
            pixmap = pixmap.scaled(*scale)

    return pixmap


def get_fbx_object_icon(fbx_object):
    icon = Qt.QtGui.QIcon(
        get_fbx_object_pixmap(fbx_object)
    )

    return icon
