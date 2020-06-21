'''Class data mapping stuff... wip

Created on 20 Mar 2019

@author: Bren
'''

import inspect
import json

import fbx
from brenpy.core import bpStr

from brenfbx.core import bfCore

# custom data type classes ---


class BpStrFbxDouble2(bpStr.BpStrFloatList):
    """Convert from string to list of floats and vice-versa.
    TODO migrate some of this back to bpStr
    """

    FROM_STR_ERR_MSG = "Failed to cast FbxDouble2 from str."

    @classmethod
    def to_str(cls, value):
        return bpStr.BpStrFloatList.to_str(value)

    @classmethod
    def from_str(cls, value):
        value = bpStr.BpStrData.from_str(value)

        if "," not in value:
            # FbxDouble3 property allows a single float to assign to all values
            # we can mimic this behaviour here
            value = [bpStr.BpStrFloat.from_str(value)]
        else:
            value = bpStr.BpStrFloatList.from_str(value)

        # check list length
        if len(value) == 0:
            raise bpStr.BpStrException(cls.FROM_STR_ERR_MSG)
        if len(value) == 1:
            value = value * 2
        else:
            value = value[:3]

        try:
            return fbx.FbxDouble2(*value)
        except:
            raise bpStr.BpStrException(cls.FROM_STR_ERR_MSG)


class BpStrFbxDouble3(bpStr.BpStrFloatList):
    """Convert from string to list of floats and vice-versa.
    TODO migrate some of this back to bpStr
    """

    FROM_STR_ERR_MSG = "Failed to cast FbxDouble3 from str."

    @classmethod
    def to_str(cls, value):
        return bpStr.BpStrFloatList.to_str(value)

    @classmethod
    def from_str(cls, value):
        value = bpStr.BpStrData.from_str(value)

        if "," not in value:
            # FbxDouble3 property allows a single float to assign to all values
            # we can mimic this behaviour here
            value = [bpStr.BpStrFloat.from_str(value)]
        else:
            value = bpStr.BpStrFloatList.from_str(value)

        # check list length
        if len(value) == 0:
            raise bpStr.BpStrException(cls.FROM_STR_ERR_MSG)
        if len(value) == 1:
            value = value * 3
        if len(value) == 2:
            value = value + [value[1]]
        else:
            value = value[:3]

        try:
            return fbx.FbxDouble3(*value)
        except:
            raise bpStr.BpStrException(cls.FROM_STR_ERR_MSG)

# data mapping globals ---


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


ATTRIBUTE_ENUM_LABELS = {
    fbx.FbxNodeAttribute.eUnknown: "unidentified",
    fbx.FbxNodeAttribute.eNull: "null",
    fbx.FbxNodeAttribute.eMarker: "marker",
    fbx.FbxNodeAttribute.eSkeleton: "skeleton",
    fbx.FbxNodeAttribute.eMesh: "mesh",
    fbx.FbxNodeAttribute.eNurbs: "nurbs",
    fbx.FbxNodeAttribute.ePatch: "patch",
    fbx.FbxNodeAttribute.eCamera: "camera",
    fbx.FbxNodeAttribute.eCameraStereo: "stereo",
    fbx.FbxNodeAttribute.eCameraSwitcher: "camera switcher",
    fbx.FbxNodeAttribute.eLight: "light",
    fbx.FbxNodeAttribute.eOpticalReference: "optical reference",
    fbx.FbxNodeAttribute.eOpticalMarker: "marker",
    fbx.FbxNodeAttribute.eNurbsCurve: "nurbs curve",
    fbx.FbxNodeAttribute.eTrimNurbsSurface: "trim nurbs surface",
    fbx.FbxNodeAttribute.eBoundary: "boundary",
    fbx.FbxNodeAttribute.eNurbsSurface: "nurbs surface",
    fbx.FbxNodeAttribute.eShape: "shape",
    fbx.FbxNodeAttribute.eLODGroup: "lodgroup",
    fbx.FbxNodeAttribute.eSubDiv: "subdiv",
}

FBX_DATA_TYPES = {
    fbx.EFbxRotationOrder: {
        #         fbx.eEulerXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerXZY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerYXZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerYZX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerZXY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerZYX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eSphericXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?
    },
    fbx.EFbxType: {
        fbx.eFbxBlob: fbx.FbxBlob,
        fbx.eFbxBool: bool,
        #     fbx.eFbxChar
        fbx.eFbxDateTime: fbx.FbxDateTime,
        #     fbx.eFbxDistance
        fbx.eFbxDouble: float,
        fbx.eFbxDouble2: fbx.FbxDouble2,
        fbx.eFbxDouble3: fbx.FbxDouble3,
        fbx.eFbxDouble4: fbx.FbxDouble4,
        #     fbx.eFbxDouble4x4 ??? fbx.FbxPropertyXMatrix
        fbx.eFbxEnum: int,  # TODO
        fbx.eFbxFloat: float,
        #     fbx.eFbxHalfFloat
        fbx.eFbxInt: int,
        fbx.eFbxLongLong: int,  # MAYBE ??????
        fbx.eFbxReference: fbx.FbxPropertyFbxReference,
        fbx.eFbxShort: int,  # MAYBE ??????
        fbx.eFbxString: str,
        fbx.eFbxTime: fbx.FbxTime,
        #     fbx.eFbxTypeCount
        fbx.eFbxUChar: unicode,  # MAYBE???
        fbx.eFbxUInt: int,  # MAYBE ??????
        fbx.eFbxULongLong: int,  # MAYBE ??????
        fbx.eFbxUShort: int,  # MAYBE ??????
        #     fbx.eFbxUndefined
    },
    fbx.EFbxQuatInterpMode: {
        #         fbx.eQuatInterpCount: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpCubic: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpOff: fbx.FbxPropertyEFbxQuatInterpMode,  # MAY
        #         fbx.eQuatInterpSlerp: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpTangentDependent: fbx.FbxPropertyEFbxQuatInter
    }
}

FBX_DATA_PYTHON_TYPES = {
    fbx.EFbxRotationOrder: {
        #         fbx.eEulerXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerXZY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerYXZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerYZX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerZXY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerZYX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eSphericXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?
    },
    "fbx.EFbxType": {
        fbx.eFbxBlob: str,  # TODO
        fbx.eFbxBool: str,
        #     fbx.eFbxChar
        fbx.eFbxDateTime: str,  # list of ints # TODO?
        #     fbx.eFbxDistance
        fbx.eFbxDouble: str,
        fbx.eFbxDouble2: str,  # list of floats # TODO?
        fbx.eFbxDouble3: str,  # list of floats # TODO?
        fbx.eFbxDouble4: str,  # list of floats # TODO?
        #     fbx.eFbxDouble4x4 ??? fbx.FbxPropertyXMatrix
        fbx.eFbxEnum: str,  # TODO
        fbx.eFbxFloat: str,
        #     fbx.eFbxHalfFloat
        fbx.eFbxInt: str,
        fbx.eFbxLongLong: str,  # MAYBE ??????
        fbx.eFbxReference: str,  # TODO
        fbx.eFbxShort: str,  # MAYBE ??????
        fbx.eFbxString: str,
        fbx.eFbxTime: str,
        #     fbx.eFbxTypeCount
        fbx.eFbxUChar: str,  # MAYBE???
        fbx.eFbxUInt: str,  # MAYBE ??????
        fbx.eFbxULongLong: str,  # MAYBE ??????
        fbx.eFbxUShort: str,  # MAYBE ??????
        #     fbx.eFbxUndefined
    },
    fbx.EFbxType: {
        fbx.eFbxBlob: str,  # TODO
        fbx.eFbxBool: bool,
        #     fbx.eFbxChar
        fbx.eFbxDateTime: list,  # list of ints # TODO?
        #     fbx.eFbxDistance
        fbx.eFbxDouble: float,
        fbx.eFbxDouble2: list,  # list of floats # TODO?
        fbx.eFbxDouble3: list,  # list of floats # TODO?
        fbx.eFbxDouble4: list,  # list of floats # TODO?
        #     fbx.eFbxDouble4x4 ??? fbx.FbxPropertyXMatrix
        fbx.eFbxEnum: str,  # TODO
        fbx.eFbxFloat: float,
        #     fbx.eFbxHalfFloat
        fbx.eFbxInt: int,
        fbx.eFbxLongLong: int,  # MAYBE ??????
        fbx.eFbxReference: str,  # TODO
        fbx.eFbxShort: int,  # MAYBE ??????
        fbx.eFbxString: str,
        fbx.eFbxTime: int,
        #     fbx.eFbxTypeCount
        fbx.eFbxUChar: unicode,  # MAYBE???
        fbx.eFbxUInt: int,  # MAYBE ??????
        fbx.eFbxULongLong: int,  # MAYBE ??????
        fbx.eFbxUShort: int,  # MAYBE ??????
        #     fbx.eFbxUndefined
    },
    fbx.EFbxQuatInterpMode: {
        #         fbx.eQuatInterpCount: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpCubic: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpOff: fbx.FbxPropertyEFbxQuatInterpMode,  # MAY
        #         fbx.eQuatInterpSlerp: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpTangentDependent: fbx.FbxPropertyEFbxQuatInter
    }
}

FBX_DATA_BPSTR_TYPES = {
    fbx.EFbxRotationOrder: {
        #         fbx.eEulerXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerXZY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerYXZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerYZX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerZXY: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eEulerZYX: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ???
        #         fbx.eSphericXYZ: fbx.FbxPropertyEFbxRotationOrder,  # MAYBE ?
    },
    fbx.EFbxType: {
        fbx.eFbxBlob: bpStr.BpStrData,  # TODO
        fbx.eFbxBool: bpStr.BpStrBool,
        #     fbx.eFbxChar
        fbx.eFbxDateTime: bpStr.BpStrData,  # list of ints # TODO?
        #     fbx.eFbxDistance
        fbx.eFbxDouble: bpStr.BpStrFloat,
        fbx.eFbxDouble2: BpStrFbxDouble2,  # list of floats # TODO set list count
        fbx.eFbxDouble3: BpStrFbxDouble3,  # list of floats # TODO set list count
        fbx.eFbxDouble4: bpStr.BpStrFloatList,  # list of floats # TODO set list count
        #     fbx.eFbxDouble4x4 ??? fbx.FbxPropertyXMatrix
        fbx.eFbxEnum: bpStr.BpStrData,  # TODO
        fbx.eFbxFloat: bpStr.BpStrFloat,
        #     fbx.eFbxHalfFloat
        fbx.eFbxInt: bpStr.BpStrInt,
        fbx.eFbxLongLong: bpStr.BpStrInt,  # MAYBE ??????
        fbx.eFbxReference: bpStr.BpStrData,  # TODO
        fbx.eFbxShort: bpStr.BpStrInt,  # MAYBE ??????
        fbx.eFbxString: bpStr.BpStrData,
        fbx.eFbxTime: bpStr.BpStrData,  # TODO
        #     fbx.eFbxTypeCount
        fbx.eFbxUChar: bpStr.BpStrData,  # MAYBE???
        fbx.eFbxUInt: bpStr.BpStrInt,  # MAYBE ??????
        fbx.eFbxULongLong: bpStr.BpStrInt,  # MAYBE ??????
        fbx.eFbxUShort: bpStr.BpStrInt,  # MAYBE ??????
        #     fbx.eFbxUndefined
    },
    fbx.EFbxQuatInterpMode: {
        #         fbx.eQuatInterpCount: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpCubic: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpOff: fbx.FbxPropertyEFbxQuatInterpMode,  # MAY
        #         fbx.eQuatInterpSlerp: fbx.FbxPropertyEFbxQuatInterpMode,  # M
        #         fbx.eQuatInterpTangentDependent: fbx.FbxPropertyEFbxQuatInter
    }
}


# Utility methods---

def get_fbx_enums():
    for i in dir(fbx):
        if i.startswith("e"):
            print i, getattr(fbx, i)


def get_fbx_data_type_objects():
    """preconfigured data type objects?
    """
    for i in dir(fbx):
        if i.endswith("DT"):
            cls = getattr(fbx, i)
            print i, cls


def get_fbx_properties():
    for i in dir(fbx):
        if i.startswith("FbxProperty"):
            print i, getattr(fbx, i)


def get_property_class(fbx_property):
    """Cast base FbxProperty as typed class.
    """
    # get property types
    prop_type_enum = fbx_property.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)

    if prop_type not in FBX_PROPERTY_TYPES:
        print "Property type not supported: {0}".format(prop_type)
        return None

    prop_type_enums = FBX_PROPERTY_TYPES[prop_type]

    if prop_type_enum not in prop_type_enums:
        print "Property type not supported: {0} {1}".format(
            fbx_property.GetName(),
            get_property_type_name(fbx_property)
        )
        return None

    prop_class = prop_type_enums[prop_type_enum]
    return prop_class


def get_property_type_name(fbx_property):
    """Get readable name from property type enum.
    """
    # get property types
    prop_type_enum = fbx_property.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)

    if prop_type not in FBX_ENUM_NAMES:
        print "Property type not supported: {0}".format(prop_type)
        return None

    prop_enum_names = FBX_ENUM_NAMES[prop_type]

    if prop_type_enum not in prop_enum_names:
        print "Property type enum not supported: {0}".format(
            fbx_property.GetName()
        )
        return None

    return prop_enum_names[prop_type_enum]


def get_enum_name(type_id, enum_id):
    return FBX_ENUM_NAMES[type_id][enum_id]


def get_fbx_object_types():
    """Return a list of all available FbxObject types
    """
    cls_types = []

    for i in dir(fbx):
        cls = getattr(fbx, i)
        if not inspect.isclass(cls):
            continue

        if issubclass(cls, fbx.FbxObject):
            cls_types.append(cls)

    return cls_types


def get_fbx_object_type_ids():
    """Return a list of FbxClassIds from all available FbxObject types.

    Note a FbxMangager must first be created for FbxClassId objects to be valid.
    Who knew?!

    """
    fbx_manager = fbx.FbxManager.Create()

    cls_type_ids = []

    for i in dir(fbx):
        cls = getattr(fbx, i)
        if not inspect.isclass(cls):
            continue

        if issubclass(cls, fbx.FbxObject):
            cls_type_ids.append(
                cls.ClassId
            )

    return cls_type_ids


def get_bpstr_data_type(fbx_property):
    """Get bpStr class suitable for FbxProperty data type
    """
    prop_type_enum = fbx_property.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)

    if prop_type not in FBX_DATA_BPSTR_TYPES.keys():
        # return string by default
        return bpStr.BpStrData

    prop_data_dict = FBX_DATA_BPSTR_TYPES[prop_type]

    if prop_type_enum not in prop_data_dict.keys():
        # return string by default
        return bpStr.BpStrData

    return prop_data_dict[prop_type_enum]


class FbxClassIdItem(object):
    """Hierarchy object with reference to FbxClassId
    """

    def __init__(self, class_id, parent=None):
        self._class_id = class_id
        self._parent = None
        self._children = []

        if parent is not None:
            self.set_parent(parent)

    def class_id(self):
        return self._class_id

    def parent(self):
        return self._parent

    def add_child(self, child):
        self._children.append(child)
        child._parent = self

    def get_child(self, child_index):
        return self._children[child_index]

    def children(self):
        return self._children

    def child_count(self):
        return len(self._children)

    def index(self):
        return self._parent._children.index(self)

    def _debug(self, indent):
        print "  " * indent, self.class_id().GetName()

    def debug(self, indent):
        self._debug(indent)

        for child in self.children():
            child.debug(indent + 1)


class FbxClassIdRoot(object):
    """Hierarchy root object with child references to all FbxClasId's

    Supports hierarchy lookup as well as flat alphabetical list.

    Overridable item class.

    TODO prevent user adding extra items?
         or other way to safely lock down items?
         (need to keep _class_id_items list in check)

    """

    def __init__(self, fbx_manager):

        if fbx_manager is None:
            fbx_manager = fbx.FbxManager.Create()

        self._fbx_manager = fbx_manager

        # populate class ids list
        self._class_id_items = []

        for i in dir(fbx):
            cls = getattr(fbx, i)
            if not inspect.isclass(cls):
                continue

            if issubclass(cls, fbx.FbxObject):
                item = self.create_item(cls.ClassId)
                self._class_id_items.append(item)

        # build hierarchy
        self._children = []

        for item in self._class_id_items:
            parent_class_id = item.class_id().GetParent()

            parent_item = self.find_item(parent_class_id)

            if parent_item is None:
                self.add_child(item)
            else:
                parent_item.add_child(item)

    def create_item(self, class_id):
        return FbxClassIdItem(class_id)

    def children(self):
        return self._children

    def add_child(self, child):
        self._children.append(child)
        child._parent = self

    def child_count(self):
        return len(self._children)

    def get_child(self, child_index):
        return self._children[child_index]

    def items(self):
        return self._class_id_items

    def item_count(self):
        return len(self._class_id_items)

    def find_item(self, class_id):
        for item in self._class_id_items:
            if item.class_id() == class_id:
                return item

        return None

    def get_item(self, item_index):
        return self._class_id_items[item_index]

    def debug(self):
        print "all: ", [self.get_item(i) for i in range(self.item_count())]
        print "class ids: ", [i.class_id().GetName() for i in self._class_id_items]
        print "root: ", [i.class_id().GetName() for i in self.children()]

        for item in self.children():
            item.debug(0)


class FbxClassIdValueItem(FbxClassIdItem):
    """Hierarchy object with reference to FbxClassId and user value
    """

    VALUE_TYPE = None

    def __init__(self, class_id, parent=None, value=None):
        super(FbxClassIdValueItem, self).__init__(class_id, parent=parent)
        self._value = None
        self.set_value(value)

    def _debug(self, indent):
        print "  " * indent, self.class_id().GetName(), self.value()

    def set_value(self, value):
        if self.VALUE_TYPE is not None:
            if not isinstance(value, self.VALUE_TYPE):
                raise bfCore.BfError(
                    "Value must be of type {} not {}".format(
                        self.VALUE_TYPE, type(value)
                    )
                )

        self._value = value

    def value(self):
        return self._value


class FbxClassIdValueRoot(FbxClassIdRoot):
    """Hierarchy root object with child reference to all FbxClassIds and user values.

    Support serialize and deserialize.

    """

    def __init__(self, fbx_manager):
        super(FbxClassIdValueRoot, self).__init__(fbx_manager)

    def create_item(self, class_id):
        item = FbxClassIdValueItem(class_id)
        return item

    def serialize(self, as_json=False, pretty=True):
        """Serialize user data to dict or json dumps.
        """
        data = {}

        for item in self.items():
            class_name = item.class_id().GetName()
            data[class_name] = item.value()

        if as_json:
            if pretty:
                data = json.dumps(
                    data,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            else:
                data = json.dumps(data)

        return data

    def deserialize(self, data):
        """Parse data and apply user values to items.
        """
        if isinstance(data, basestring):
            data = json.loads(data)

        for class_name, value in data.iteritems():
            class_id = self._fbx_manager.FindClass(class_name)

            if not class_id.IsValid():
                print "[ WARNING ] No class found: {}".format(class_name)
                continue

            class_item = self.find_item(class_id)
            class_item.set_value(value)

        return True

    def find_items_by_value(self, value):
        """Return a list of items with matching value
        """
        matching_items = []

        for item in self._class_id_items:
            if item.value() == value:
                matching_items.append(item)

        return matching_items


class FbxClassIdBoolItem(FbxClassIdValueItem):
    """Hierarchy object with reference to FbxClassId and user value
    """

    VALUE_TYPE = bool

    def __init__(self, class_id, parent=None, value=True):
        super(FbxClassIdBoolItem, self).__init__(
            class_id, parent=parent, value=value
        )


class FbxClassIdBoolRoot(FbxClassIdValueRoot):
    """Hierarchy root object with child reference to all FbxClassIds and user values.

    Support serialize and deserialize.

    """

    def __init__(self, fbx_manager):
        super(FbxClassIdBoolRoot, self).__init__(fbx_manager)

    def create_item(self, class_id):
        item = FbxClassIdBoolItem(class_id)
        return item



# TESTING
if __name__ == "__main__":
    fbx_manager = fbx.FbxManager.Create()
    test = FbxClassIdRoot(fbx_manager)
    test.debug()

    test_2 = FbxClassIdValueRoot(fbx_manager)
    test_2.debug()
    data = test_2.serialize(as_json=True, pretty=True)
    print data

    print test_2.deserialize(data)

    test_3 = FbxClassIdBoolRoot(fbx_manager)
    test_3.debug()
    data = test_3.serialize(as_json=True, pretty=True)
    print data

    print test_3.deserialize(data)

    test_3.debug()

#     get_fbx_object_type_ids()
#     print get_fbx_data_type_objects()
