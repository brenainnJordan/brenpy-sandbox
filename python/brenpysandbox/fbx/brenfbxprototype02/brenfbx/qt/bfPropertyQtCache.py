"""
"""

import sys

import os
import fbx
import FbxCommon
import inspect
from types import NoneType

from brenfbx.core import bfIO
from brenfbx.core import bfData
from brenfbx.core import bfUtils
from brenfbx.core import bfCore

from brenpy.cg import bpEuler
from brenpy.utils import bpStr

# from brenrig.sandbox import fbx_prototype_01
from brenfbx.core import bfObject
from brenfbx.core import bfProperty
from brenfbx.qt import bfQtCore


class BfPropertyId(object):
    def __init__(self, value=0, fbx_object_id=0):
        super(BfPropertyId, self).__init__()

        self._value = value
        self._fbx_object_id = fbx_object_id

    def value(self):
        return self._value

    def fbx_object_id(self):
        return self._fbx_object_id


class BfPropertyConId(BfPropertyId):
    """Id object for connection models
    """

    def __init__(self, value=0, fbx_object_id=0):
        super(BfPropertyConId, self).__init__(
            value=value, fbx_object_id=fbx_object_id
        )

# class BfIdDummyData(object):
#     def __init__(self, init_value=0):
#         super(BfIdDummyData, self).__init__()
#
#         self._value = init_value
#
#     def value(self):
#         return self._value
#
#     def set_value(self, value):
#         self._value = value


class BFbxPropertyRoot(object):
    """Custom hierarchy object to represents object that owns all child properties.
    """

    def __init__(self, fbx_property_root):
        super(BFbxPropertyRoot, self).__init__()

        self._children = []

        self._property_object = fbx_property_root

        self._unique_id = None

    def children(self):
        return self._children

    def fbx_object(self):
        return self.fbx_property().GetFbxObject()

    def property_object(self):
        return self._property_object

    def fbx_property(self):
        return self.property_object().Property()

    def child_count(self):
        return len(self._children)

    def get_child(self, child_index):
        if child_index >= self.child_count():

            raise bfCore.BFbxError(
                "Child index out of range: {} ({}.{})".format(
                    child_index,
                    self.fbx_object().GetName(),
                    self.fbx_property().GetName()
                )
            )

        return self._children[child_index]

    def add_child(self, child):

        self._children.append(child)

        child.set_parent(self)

    def get_child_index(self, child):
        if child not in self._children:
            return None

        return self._children.index(child)

    def is_root(self):
        return True

    def key(self):
        return "{}".format(
            self.fbx_object().GetUniqueID(),
        )

    def unique_id(self):
        return self._unique_id

    def debug(self, item=None, indent=1):
        if item is None:
            item = self

        if indent == 1:
            print "Property Root debug:"
            print "  ", self.key(), self.property_object().GetName()

        for child in item.children():
            print "  " * (indent + 1), child.unique_id(), child.key(), child.property_object().GetName()

            self.debug(child, indent + 1)


class BFbxPropertyItem(BFbxPropertyRoot):
    """Custom hierarchy object to represent property or property component.

    TODO when introducing property children,
    we will need to store an additional parameter for say "context index"
    to differentiate hierarchy index from property child or component index.

    Doing so will also free us to swap components and children without breaking
    structure.

    TODO components needs some rethinking
         currently slightly broken
         maybe we can have sourceObjects and sourceProperties "dummy" items
         and sourceObject and sourceProperty item subclasses under them
         if the dummy items have no children we can filter out those items
         to tidy up the property view,
         but we'd need a simple mechanism to bring them back
         when adding new source objects or properties.

    """

    def __init__(self, property_object):
        super(BFbxPropertyItem, self).__init__(property_object)

        self._parent = None

#         self._property_index = property_index

    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def get_index(self):
        return self._parent.get_child_index(self)

    def is_root(self):
        return False

    def get_index_path(self):
        index_path = []

        item = self

        while not item.is_root():
            index_path.insert(0, item.get_index())
            item = item.parent()

        return index_path

    def key(self):
        return "{}_{}".format(
            self.fbx_object().GetUniqueID(),
            self.unique_id()
        )


#     def contextual_index(self):
#         return self._contextual_index

    def get_root(self):
        parent = self._parent

        while parent is not None:
            #             if isinstance(parent, BFbxPropertyRoot):
            if parent.is_root():
                return parent

            parent = parent.getParent()

        raise bfCore.BFbxError("Unable to find property root")


"""
need classes for:

BFbxPropertyConnectionBase
BFbxPropertyConnectionsBase

BFbxPPConnection
BFbxPPConnections

BFbxOPConnection
BFbxOPConnections


More stuff to think about:

- how do we keep property model in sync with scene model
  for example say we change the name of an object that is 
  a connection of a property, how should the scene model
  inform the property model that the name has changed???
- or if a connected object is deleted?
- or if a connected property is renamed or deleted?
- or if the object of a connected property is renamed or deleted?


** Let's shelve this idea for now **

There's a good chance that creating a "convenient" hierarchy
could cause more problems than it solves.

In the case of displaying connection relationships in the rigging system
this will likely use custom widgets anyway, that can display the
conveniences we need.

The foundation should remain generic.

This does mean that we will need more views/widgets to display all the connections,
but at least doing so will be clean.

"""

#
# class BFbxPropertyConnectionBase(object):
#     def __init__(self, property_item, connection_index):
#         super(BFbxPropertyConnectionBase, self).__init__()
#
#         self._parent = property_item
#         self._connection_index = connection_index
#         self._unique_id = None
#
#     def connection_index(self):
#         return self._connection_index
#
#     def property_object(self):
#         return self._property_item.property_object()
#
#     def parent(self):
#         return self._property_item
#
#     def set_parent(self, parent):
#         self._parent = parent
#
#     def get_index(self):
#         return self._parent.get_child_index(self)
#
#     def unique_id(self):
#         return self._unique_id
# #
# # class BFbxPropertyConnectionsBase(BFbxPropertyItem):
# #     def __init__(self, fbx_object, property_object, contextual_index):
# #         super(BFbxPropertyConnectionsBase, self).__init__(
# #             fbx_object, property_object, contextual_index
# #         )
#
#
# class BFbxPPConnection(BFbxPropertyConnectionBase):
#     def __init__(self, property_item, connection_index):
#         super(BFbxPPConnection, self).__init__(
#             property_item, connection_index
#         )
#
# #
# # class BFbxPPConnections(BFbxPropertyItem):
# #     def __init__(self, fbx_object, property_object, contextual_index):
# #         super(BFbxPPConnections, self).__init__(
# #             fbx_object, property_object, contextual_index
# #         )
#
#
# # class BFbxOPConnections(BFbxPropertyItem):
# #     def __init__(self, fbx_object, property_object, contextual_index):
# #         super(BFbxOPConnections, self).__init__(
# #             fbx_object, property_object, contextual_index
# #         )
#
#
# class BFbxOPConnection(BFbxPropertyConnectionBase):
#     def __init__(self, property_item, connection_index):
#         super(BFbxOPConnection, self).__init__(
#             property_item, connection_index
#         )


class BFbxPropertyCache(object):
    """Stores a temporary cache of all properties for an FbxObject.

    Uses custom hierarchy.

    """

    def __init__(self, fbx_object):
        super(BFbxPropertyCache, self).__init__()

        self._fbx_object = fbx_object
        self._id_data = {}
        self._id_objects = {}
        self._id_con_objects = {}
        self._component_data = {}
        self._root = None

        if isinstance(fbx_object, fbx.FbxObject):

            self.create_property_hierarchy(
                fbx_object
            )

    def fbx_object(self):
        return self._fbx_object

    def root(self):
        return self._root

    def assign_unique_id(self, item):
        """Assigns unique id to property item.
        """
#         if len(self._id_data):
#             uid = max(self._id_data.keys()) + 1
#         else:
#             uid = 0

        uid = bfUtils.get_fbx_property_object_index(
            item.fbx_property()
        )

        fbx_object_id = item.fbx_object().GetUniqueID()

        item._unique_id = uid
        self._id_data[uid] = item

        id_object = BfPropertyId(uid, fbx_object_id)
        self._id_objects[uid] = id_object

        id_con_object = BfPropertyConId(uid, fbx_object_id)
        self._id_con_objects[uid] = id_con_object

        return uid

    def get_item_from_unique_id(self, uid):
        if uid not in self._id_data.keys():
            return None

        return self._id_data[uid]

    def get_id_value(self, value):
        if isinstance(value, BFbxPropertyRoot):
            uid = value.unique_id()

        elif isinstance(value, (int, long)):
            uid = value

        else:
            raise bfQtCore.BfQtError(
                "Failed to retreive unique id: {}".format(value)
            )

        return uid

    def get_id_object(self, value):

        uid = self.get_id_value(value)

        if uid not in self._id_objects:
            raise bfQtCore.BfQtError(
                "Failed to get id object: {} {}".format(
                    uid, value
                )
            )

        return self._id_objects[uid]

    def get_id_con_object(self, value):

        uid = self.get_id_value(value)

        if uid not in self._id_con_objects:
            raise bfQtCore.BfQtError(
                "Failed to get id con object: {} {}".format(
                    uid, value
                )
            )

        return self._id_con_objects[uid]

    def add_property_child(self, fbx_property, parent_item):
        """Recursively add child components and child properties.
        """

        # TODO (find specific Fn class)
        property_fn = bfProperty.BFbxProperty(fbx_property)

        if not property_fn.IsValid():
            print "Failed to initialize property Fn: {}.{}".format(
                self.fbx_object().GetName(), fbx_property.GetName()
            )
            return False

        property_item = BFbxPropertyItem(
            property_fn
        )

        self.assign_unique_id(property_item)

        parent_item.add_child(property_item)

        # add child properties
        for child_property in bfUtils.get_child_properties(fbx_property):
            self.add_property_child(child_property, property_item)

    def create_property_hierarchy(self, fbx_object):
        """Create full customised property hierarchy.

        Includes property 'components' aka InputReferenceArrayProperty input objects.

        TODO add to QtModel.

        """

        root_property_fn = bfProperty.BFbxProperty(fbx_object.RootProperty)
        self._root = BFbxPropertyRoot(root_property_fn)
        self.assign_unique_id(self._root)

        for fbx_property in bfUtils.get_root_properties(fbx_object):
            self.add_property_child(fbx_property, self._root)

#         root.debug()

        return True


def property_test(fbx_file):
    #     fbx_manager = fbx.FbxManager.Create()
    #     fbx_scene = fbx.FbxScene.Create(fbx_manager, "scene")
    #     fbx_object = fbx.FbxObject.Create(fbx_manager, "test")
    #
    #     fbx_scene.ConnectSrcObject(fbx_object)

    fbx_scene, fbx_manager = bfIO.load_file(
        fbx_file,
        fbx_manager=None,
        settings=None,
        verbose=True,
        err=True
    )

#     fbx_object = fbx_scene.GetRootNode()

    fbx_object = fbx_scene.FindSrcObject("object1")

    cache = BFbxPropertyCache(fbx_object)

    cache.root().debug()


if __name__ == "__main__":
    DUMP_DIR = r"D:\Repos\dataDump\brenrig"
    TEST_FILE = "fbx_property_hierarchy_test_01.fbx"
    TEST_PATH = os.path.join(DUMP_DIR, TEST_FILE)

    property_test(TEST_PATH)
