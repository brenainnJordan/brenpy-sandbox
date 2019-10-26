"""FBX utility functions and classes.

"""

import fbx

from brenfbx.core import bfData

from brenpy.utils import bpStr


# create methods ---


def create_skeleton_root_node(root_name, fbx_manager, parent=None):
    """Convenience method to create a skeleton root node.
    """
    root_attr = fbx.FbxSkeleton.Create(fbx_manager, root_name)
    root_attr.SetSkeletonType(fbx.FbxSkeleton.eRoot)

    node = fbx.FbxNode.Create(fbx_manager, root_name)
    node.SetNodeAttribute(root_attr)

    if parent is not None:
        parent.AddChild(node)

    return node


def create_skeleton_limb_node(joint_name, fbx_manager, parent=None):
    """Convenience method to create a skeleton node.
    """
    node = fbx.FbxNode.Create(fbx_manager, joint_name)

    skel_attr = fbx.FbxSkeleton.Create(
        fbx_manager, joint_name
    )

    skel_attr.SetSkeletonType(fbx.FbxSkeleton.eLimbNode)
    node.SetNodeAttribute(skel_attr)

    # activate preRotation etc.
    node.SetRotationActive(True)

    if parent is not None:
        parent.AddChild(node)

    return node


def create_null(name, fbx_manager, parent=None):
    """Convenience method to create a null node.
    """
    node = fbx.FbxNode.Create(fbx_manager, name)

    null_attr = fbx.FbxNull.Create(fbx_manager, name)
    null_attr.Look.Set(fbx.FbxNull.eNone)
    node.SetNodeAttribute(null_attr)

    if parent is not None:
        parent.AddChild(node)

    return node


def create_locator(name, fbx_manager, parent=None):
    """Convenience method to create a null node.
    """
    node = fbx.FbxNode.Create(fbx_manager, name)

    null_attr = fbx.FbxNull.Create(fbx_manager, name)
    null_attr.Look.Set(fbx.FbxNull.eCross)
    node.SetNodeAttribute(null_attr)

    if parent is not None:
        parent.AddChild(node)

    return node


# query methods ---
def get_connected_index(src_object, dst_object, criteria=None):

    if criteria is not None:
        src_count = src_object.GetSrcObjectCount(criteria)

        for i in range(src_count):
            src_object.GetSrcObjectCount(criteria, i)
            if src_object is dst_object:
                return i
    else:
        src_count = src_object.GetSrcObjectCount()

        for i in range(src_count):
            src_object.GetSrcObjectCount(i)
            if src_object is dst_object:
                return i

    return None


def get_fbx_node_index(fbx_node):
    """Find node in parent and return index.
    """
    if not isinstance(fbx_node, fbx.FbxNode):
        # TODO raise?
        return None

    parent = fbx_node.GetParent()

    if parent is None:
        return None

    for i in range(parent.GetChildCount()):
        if parent.GetChild(i) is fbx_node:
            return i

    # if we get to this point, somethings gone wrong!
    raise Exception("Failed to find parent: {0}".format(fbx_node.GetName()))


def get_fbx_node_attribute_label(fbx_node):
    """Return convinient name for fbx node attribute."""

    fbx_attribute = fbx_node.GetNodeAttribute()
    enum_id = fbx_attribute.GetAttributeType()

    if not enum_id in bfData.ATTRIBUTE_ENUM_LABELS:
        return ""
    else:
        return bfData.ATTRIBUTE_ENUM_LABELS[enum_id]


def get_unique_name(name, scene):
    """Find name unique to scene.
    """

    scene_names = []

    for i in range(scene.GetSrcObjectCount()):
        src = scene.GetSrcObject(i)
        scene_names.append(src.GetName())

        if src.GetName() == "guide_1":
            print src, src.GetName()

    i = 0
    unique_name = "{}_{}".format(name, i)

    while unique_name in scene_names:
        i += 1
        unique_name = "{}_{}".format(name, i)

    return unique_name


# property data utils ---


def get_property_name(fbx_property):
    name = fbx_property.GetName()
    # GetName() returns a fbx.FbxString
    # so we should convert to str first
    return str(name)


def get_property_value_as_str(fbx_property):
    """Get property value and convert to str using BrStr.
    """
    value = fbx_property.Get()

    data_cls = get_property_bpStr_type(fbx_property)
    value = data_cls.to_str(value)
    return value


def get_property_value_as_py(fbx_property):
    """Get property value and convert to suitable standard python data type.
    """
    value = fbx_property.Get()
    data_cls = get_property_py_type(fbx_property)
    value = data_cls(value)
    return value


def get_property_value_from_str(fbx_property, value):
    """Convert value to data suitable to be passed to property.

    Assumes that str data can be converted to type expected by property.
    """

    data_cls = get_property_bpStr_type(fbx_property)

    try:
        value = data_cls.from_str(value)

    except bpStr.BpStrException as err:
        raise err

    return value


def set_property_value_from_str(fbx_property, value):
    """Set fbx property from str data.

    Assumes that str data can be converted to type expected by property.
    """

    data_cls = get_property_bpStr_type(fbx_property)(fbx_property)

    try:
        value = data_cls.from_str(value)

    except bpStr.BpStrException as err:
        print err.message
        return False

    return fbx_property.Set(value)


def get_property_py_type(cls, fbx_property):
    """Get suitable standard python type for fbx_property data type.
    """

    prop_type_enum = fbx_property.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)

    if prop_type not in bfData.FBX_DATA_PYTHON_TYPES.keys():
        # return string by default
        return str

    prop_data_dict = bfData.FBX_DATA_PYTHON_TYPES[prop_type]

    if prop_type_enum not in prop_data_dict.keys():
        # return string by default
        return str

    return prop_data_dict[prop_type_enum]


def get_property_bpStr_type(fbx_property):
    """Get BrStr class suitable for converting data to and from property data type.
    """
    prop_type_enum = fbx_property.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)

    if prop_type not in bfData.FBX_DATA_BPSTR_TYPES.keys():
        # return string by default
        return bpStr.BpStrData

    prop_data_dict = bfData.FBX_DATA_BPSTR_TYPES[prop_type]

    if prop_type_enum not in prop_data_dict.keys():
        # return string by default
        return bpStr.BpStrData

    return prop_data_dict[prop_type_enum]


def get_property_type_str(fbx_property):
    """Get string representation of fbx_property type.
    """
    prop_type_enum = fbx_property.GetPropertyDataType().GetType()
    prop_type = type(prop_type_enum)

    if prop_type not in bfData.FBX_PROPERTY_TYPES:
        return "unknownType_{}".format(prop_type)

    prop_enum_names = bfData.FBX_ENUM_NAMES[prop_type]

    if prop_type_enum not in prop_enum_names:
        return "unknownEnum_{}_{}".format(prop_type, prop_type_enum)

    return prop_enum_names[prop_type_enum]


# property hierarchy utils ---

def get_root_properties_old(fbx_object):
    """Return a list of root-level properties.
    """

    root_properties = []

    fbx_property = fbx_object.GetFirstProperty()

    while fbx_property.IsValid():
        if fbx_property.GetParent().IsRoot():
            root_properties.append(fbx_property)

        fbx_property = fbx_object.GetNextProperty(fbx_property)

    return root_properties


def get_child_properties(fbx_property):
    """Return a list of child properties.
    """
    child_properties = []

    child_property = fbx_property.GetChild()

    while child_property.IsValid():
        child_properties.append(child_property)
        child_property = child_property.GetSibling()

    return child_properties


def get_root_properties(fbx_object):
    """Return a list of root-level properties.
    """
    root_properties = get_child_properties(
        fbx_object.RootProperty
    )

    return root_properties


def get_fbx_property_object_index(fbx_property):
    """Find property under owner object and return index.
    """

    if fbx_property.IsRoot():
        return -1

    fbx_object = fbx_property.GetFbxObject()

    i = 0
    prop = fbx_object.GetFirstProperty()

    while prop.IsValid():
        if prop == fbx_property:
            return i

        i += 1
        prop = fbx_object.GetNextProperty(prop)

    return None


def get_fbx_property_index(fbx_property):
    """Find property under parent property and return index.
    """

    parent_property = fbx_property.GetParent()
    child_properties = get_child_properties(parent_property)
    property_index = child_properties.index(fbx_property)

    return property_index


def get_fbx_property_index_path(fbx_property):
    """Get chain of property indices leading to fbx_property
    """

    index_path = []

    while not fbx_property.GetParent().IsRoot():
        index_path.append(
            get_fbx_property_index(fbx_property)
        )

        fbx_property = fbx_property.GetParent()

    return index_path


def get_fbx_property_unique_id_merked(fbx_property):
    """Construct an id for this property unique under owner object.
    ** not unique **
    use property object index instead!
    """
    index_path = get_fbx_property_index_path(fbx_property)
    unique_id = int("".join(list(map(str, index_path))))

    return unique_id
