"""Dynamic item implementation for FbxConnections


** DEPRICATED **

See bfConnectionUtilityItems

TODO
    items that store references to connected FbxObject or FbxProperty.
    Alternatively we could in theory only store the uniqueID and/or the property index
    and get the object from the scene model, and get the property from the object.
    This would be cleaner, and safer in case an object or property is deleted (potentially less crashes)
    but slower as it would need to look up the object/property every time we query data
    which would be highly inefficient.


TODO ok, we need to re-think this slightly,
    there is no reliability on connection indices,
    meaning we cannot safely implement dynamically re-ordering connections
    or implementing undo.
    Instead what we should do is revert to the old connection model for adding or removing connections,
    because those are simple and safe operations.
    (although what does that mean if an object is connected more than once?)
    When we want to re-order connections we instead approach this as a "utility operation",
    we can use the item methods, and even use undo in this context, but connections will not be
    edited until the operation is "applied".
    The output of the item manager will be a new order of connected objects or properties,
    all connections will be removed, then reconnected in the new order.
    This would likely be done in a dialog context to avoid any other operations like
    creating or destroying objects potentially distrupting the process.

"""

import fbx
import types

import brenfbx.test.bfTestBase
import brenfbx.utils.fbx_utils.bfFbxConnectionUtils
from brenpy.core import bpType
from brenpy.core import bpObject
# from brenpy.items import bpValueItems

from brenfbx.core import bfCore
from brenfbx.core import bfFbxRegister

from brenfbx.items import bfItems
from brenfbx.items import bfSceneItems
from brenfbx.items import bfPropertyItems
# bfPropertyItems.BfFbxPropertyItem

from brenfbx.utils import bfObjectUtils
from brenfbx.utils.fbx_utils import bfFbxUtils


class BfConnectionItem(bfItems.BfValueItem):
    """Base class for all connection items

    In theory this could be used to construct a hierarchy of connections,
    but considering how easy it is to create cyclic connections in fbx,
    it's probably best not to.

    Instead a "root" item should be defined, with children of a specific type of connection,
    eg srcObjects, and it's children should not allow it's own children,
    in order to prevent the user from inadvertently creating a hierarchy.

    """

    def __init__(self, *args, **kwargs):
        super(BfConnectionItem, self).__init__(*args, **kwargs)

    def editable(self, *args, **kwargs):
        return False

    def connectible_obj(self):
        """Overridible method
        """
        return None

    def valid(self):
        return self.connectible_obj() is not None

    @classmethod
    def fbx_connect(cls, connected_obj, value):
        """Overridable method to create new connection
        """
        pass

    @classmethod
    def fbx_disconnect_indices(cls, connected_obj, indices):
        """*overidable method"""
        return True

    def add_child(self, child):

        # TODO fix this!! (not being called)
        #       inherit from value item to fix (hopefully?!)

        print "add child"
        # TODO parse arg

        if not self.valid():
            raise bfCore.BfError("Connection item invalid, cannot add child")
        if not child.valid():
            raise bfCore.BfError("Child connection item invalid, cannot add child: {}".format(child))

        res = super(BfConnectionItem, self).add_child(child)

        if res:
            # make new connection
            if not self.item_manager().is_rebuilding():
                print "calling fbx connect"
                self.fbx_connect(self.connectible_obj(), child.connectible_obj())
            else:
                print "stuff?"
        else:
            print "ARSE"

        return res

    def remove_child(self, child, default_to_root=False):

        # TODO parse arg

        if not self.valid():
            raise bfCore.BfError("Connection item invalid, cannot remove child")
        if not child.valid():
            raise bfCore.BfError("Child connection item invalid, cannot remove child: {}".format(child))

        child_index = child.get_index()

        res = super(BfConnectionItem, self).remove_child(child, default_to_root=default_to_root)

        if res:
            # remove connection
            if not self.item_manager().is_rebuilding():
                self.fbx_disconnect_indices(self.connectible_obj(), [child_index])

        return res


class BfFbxObjectConnectionItem(BfConnectionItem):
    def __init__(self, *args, **kwargs):
        super(BfFbxObjectConnectionItem, self).__init__(*args, **kwargs)

    def define_type_rules(self):
        type_rules = bpType.BpTypeRules(
            (int, long),
            allow_classes=False,
            allow_instances=True,
            allow_subclasses=True,
            label="BfFbxObjectConnectionItem"
        )

        return type_rules

    def connectible_obj(self):
        """Overridible method
        """
        return self.fbx_register().get_fbx_object(self.value())


class BfFbxPropertyConnectionItem(BfConnectionItem):
    def __init__(self, *args, **kwargs):
        super(BfFbxPropertyConnectionItem, self).__init__(*args, **kwargs)

    def define_type_rules(self):
        type_rules = bpType.BpTypeRules(
            bfFbxRegister.BfFbxPropertyId,
            allow_classes=False,
            allow_instances=True,
            allow_subclasses=True
        )

        return type_rules

    def connectible_obj(self):
        """Overridible method
        """
        return self.fbx_register().get_fbx_property(self.value())


class BfConnectionRootItemBase(
    # BfConnectionItemBase,
    # bpValueItems.BpValueItem
    bfItems.BfValueItem
):
    """Item to represent the FbxObject or FbxProperty to query, add or remove connections.
    """

    # VALUE_REFERENCE = bfItemValueReferences.BfConnectedObjValueReference

    def __init__(self, *args, **kwargs):
        super(BfConnectionRootItemBase, self).__init__(*args, **kwargs)

    # def define_type_rules(self):
    #     type_rules = bpObject.BpTypeRules(
    #         (fbx.FbxObject, fbx.FbxProperty, types.NoneType),
    #         allow_classes=False,
    #         allow_instances=True,
    #         allow_subclasses=True
    #     )
    #
    #     return type_rules

    # def connectible_obj(self):
    #     return self.value()

    # def editable(self, *args, **kwargs):
    #     return False

    @classmethod
    def fbx_connect(cls, connected_obj, value):
        """Overridable method to create new connection
        """
        pass

    @classmethod
    def fbx_disconnect_indices(cls, connected_obj, indices):
        """*overidable method"""
        return True

    def add_child(self, child):

        # TODO fix this!! (not being called)
        #       inherit from value item to fix (hopefully?!)

        print "add child"
        if not self.connectible_obj():
            print "BLAH"
            return True

        res = super(BfConnectionItemBase, self).add_child(child)

        if res:
            # make new connection
            if not self.item_manager().is_rebuilding():
                print "calling fbx connect"
                self.fbx_connect(self.connectible_obj(), child.connectible_obj())
            else:
                print "stuff?"
        else:
            print "ARSE"

        return res

    def remove_child(self, child, default_to_root=False):
        if not self.connectible_obj():
            return True

        child_index = child.get_index()

        res = super(BfConnectionItemBase, self).remove_child(child, default_to_root=default_to_root)

        if res:
            # remove connection
            if not self.item_manager().is_rebuilding():
                self.fbx_disconnect_indices(self.connectible_obj(), [child_index])

        return res


class BfSrcObjectsRootItem(BfConnectionRootItemBase):
    def __init__(self, *args, **kwargs):
        super(BfSrcObjectsRootItem, self).__init__(*args, **kwargs)

    @classmethod
    def fbx_connect(cls, connected_obj, fbx_object):
        res = connected_obj.ConnectSrcObject(fbx_object)
        return res

    @classmethod
    def fbx_disconnect_indices(cls, connected_obj, indices):
        return brenfbx.utils.fbx_utils.bfFbxConnectionUtils.BfDisconnectIndices.src_objects(connected_obj, indices)


class BfDstObjectsRootItem(BfConnectionRootItemBase):
    def __init__(self, *args, **kwargs):
        super(BfDstObjectsRootItem, self).__init__(*args, **kwargs)

    @classmethod
    def fbx_connect(cls, connected_obj, fbx_object):
        res = connected_obj.ConnectDstObject(fbx_object)
        return res

    @classmethod
    def fbx_disconnect_indices(cls, connected_obj, indices):
        return brenfbx.utils.fbx_utils.bfFbxConnectionUtils.BfDisconnectIndices.dst_objects(connected_obj, indices)


class BfSrcPropertiesRootItem(BfConnectionRootItemBase):
    def __init__(self, *args, **kwargs):
        super(BfSrcPropertiesRootItem, self).__init__(*args, **kwargs)

    @classmethod
    def fbx_connect(cls, connected_obj, fbx_property):
        res = connected_obj.ConnectSrcProperty(fbx_property)
        return res

    @classmethod
    def fbx_disconnect_indices(cls, connected_obj, indices):
        return brenfbx.utils.fbx_utils.bfFbxConnectionUtils.BfDisconnectIndices.src_properties(connected_obj, indices)


class BfDstPropertiesRootItem(BfConnectionRootItemBase):
    def __init__(self, *args, **kwargs):
        super(BfDstPropertiesRootItem, self).__init__(*args, **kwargs)

    @classmethod
    def fbx_connect(cls, connected_obj, fbx_property):
        res = connected_obj.ConnectDstProperty(fbx_property)
        return res

    @classmethod
    def fbx_disconnect_indices(cls, connected_obj, indices):
        return brenfbx.utils.fbx_utils.bfFbxConnectionUtils.BfDisconnectIndices.dst_properties(connected_obj, indices)


# class BfFbxObjectConnectionItem(
#     # BfConnectionItemBase,
#     # bfSceneItems.BfObjectItem
#     bfItems.BfValueItem
# ):
#     """Item to represent a connection from an FbxObject
#     """
#     # TODO FIX THIS !! (don't use object item)
#     def __init__(self, *args, **kwargs):
#         super(BfFbxObjectConnectionItem, self).__init__(*args, **kwargs)
#
#     def editable(self, *args, **kwargs):
#         return False
#
#     def connectible_obj(self):
#         return self.fbx_object()
#
# class BfFbxPropertyConnectionItem(
#     # BfConnectionItemBase,
#     # bfPropertyItems.BfFbxPropertyItem
#     bfItems.BfValueItem
# ):
#     """Item to represent a connection from an FbxProperty
#     """
#     # TODO FIX THIS !! (don't use property item)
#     def __init__(self, *args, **kwargs):
#         super(BfFbxPropertyConnectionItem, self).__init__(*args, **kwargs)
#
#     def editable(self, *args, **kwargs):
#         return False
#
#     def connectible_obj(self):
#         return self.fbx_property()


class BfConnectionsItemManagerBase(
    # brenfbx.core.bfEnvironment.BfEnvironmentDependant,
    # bpValueItems.BpValueItemManager
    bfItems.BfValueItemManager
):
    """TODO/WIP
    """

    # ROOT_ITEM_CLS = BfConnectionRootItemBase

    # ITEM_CLS = BfConnectionItem

    def __init__(self, *args, **kwargs):
        super(BfConnectionsItemManagerBase, self).__init__(*args, **kwargs)
        self._connected_obj = None

    def connected_obj(self):
        return self._connected_obj

    def set_connected_obj(self, value):

        if not isinstance(value, (fbx.FbxObject, fbx.FbxProperty, types.NoneType)):
            raise bfCore.BfError(
                "connected obj must be instance of FbxObject or FbxProperty"
            )

        self._connected_obj = value

        self.rebuild()

        return True

    def get_fbx_object(self):
        if self.connected_obj() is None:
            return None

        elif isinstance(self.connected_obj(), fbx.FbxProperty):
            return self.connected_obj().GetFbxObject()

        elif isinstance(self.connected_obj(), fbx.FbxObject):
            return self.connected_obj()

        else:
            raise bfCore.BfError(
                "Failed to get FbxObject"
            )

    def get_fbx_scene(self):
        fbx_object = self.get_fbx_object()
        return fbx_object.GetScene()

    # def _disconnect_indices(self, indices):
    #     """*overidable method"""
    #     return True

    # def destroy_item(self, item, recursive=True, disconnect_fbx_obj=True):
    #     """
    #     """
    #     item_index = item.get_index()
    #     res = super(BfConnectionsItemManagerBase, self).destroy_item(item, recursive=recursive)
    #
    #     if not res:
    #         return res
    #
    #     # if disconnect_fbx_obj:
    #     #     # self.reset()
    #     #     self._disconnect_indices([item_index])
    #     #     # self.rebuild()
    #
    #     return res

    #
    # @classmethod
    # def _fbx_connect(cls, connected_obj, value):
    #     """Overridable method to create new connection
    #     """
    #     pass

    def create_connection(self, value):
        """Create new connection
        """
        print "CREATE CON", value
        if self.connected_obj() is None:
            return False

        # res = self._fbx_connect(self.connected_obj(), value)

        res = self.create_item(value=value)

        return res

    def _fbx_disconnect_all(self):
        """Overridable method to disconnect all source objects/properties
        """
        pass

    def fbx_disconnect_all(self):
        """Disconnect all source objects/properties
        """
        if self.connected_obj() is None:
            return False

        res = self._fbx_disconnect_all()

        self.rebuild()

        return res

    def create_item(self, value=None, unique_id=None):
        """Stuff
        """
        print "CREATE POOP", value, self.root_item()

        item = super(BfConnectionsItemManagerBase, self).create_item(
            value=value,
            unique_id=unique_id
        )

        self.root_item().add_child(item)

        # item.properties().set_parent_locked(True)
        item.properties().set_children_locked(True)

        return item

    def connection_count(self):
        if self.connected_obj() is None:
            return 0
        else:
            return self.get_connection_count(self.connected_obj())

    @classmethod
    def get_connection_count(cls, connected_object):
        """Overidable method
        """
        return 0

    @classmethod
    def get_connection(cls, connected_object, index):
        """Overridable method to get srs/dst object/property connection
        """
        return None

    def _rebuild(self):
        """
        Notes:
            Unlike the scene item manager, we don't use the fbx unique ID,
            this is because we may find the same object connected more than once,
            so each instance will need it's own ID.

        """

        if self.connected_obj() is None:
            return True

        self.root_item().set_value(self.connected_obj())

        for i in range(self.get_connection_count(self.connected_obj())):
            object_connection = self.get_connection(self.connected_obj(), i)
            self.create_item(value=object_connection, unique_id=None)

        return True


class BfFbxObjectConnectionsManager(BfConnectionsItemManagerBase):
    """
    """

    ITEM_CLS = BfFbxObjectConnectionItem

    def __init__(self, *args, **kwargs):
        super(BfFbxObjectConnectionsManager, self).__init__(*args, **kwargs)

    def create_item(self, value=None, unique_id=None):
        """Stuff
        """

        # assuming value is FbxObject
        item = super(BfFbxObjectConnectionsManager, self).create_item(
            value=value.GetUniqueID(), unique_id=unique_id
        )

        return item


class BfFbxPropertyConnectionsManager(BfConnectionsItemManagerBase):
    """
    """

    ITEM_CLS = BfFbxPropertyConnectionItem

    def __init__(self, *args, **kwargs):
        super(BfFbxPropertyConnectionsManager, self).__init__(*args, **kwargs)

    # def create_item(self, value=None, unique_id=None):
    #     """Stuff
    #     """
    #
    #     item = super(BfFbxPropertyConnectionsManager, self).create_item(
    #         value=value,
    #         unique_id=unique_id
    #     )
    #
    #     # self.root_item().add_child(item)
    #
    #     # item.properties().set_parent_locked(True)
    #     # item.properties().set_children_locked(True)
    #
    #     return item


class BfFbxSrcObjectsManager(BfFbxObjectConnectionsManager):
    ROOT_ITEM_CLS = BfSrcObjectsRootItem

    def __init__(self, *args, **kwargs):
        super(BfFbxSrcObjectsManager, self).__init__(*args, **kwargs)

    @classmethod
    def get_connection_count(cls, connected_obj):
        return connected_obj.GetSrcObjectCount()

    @classmethod
    def get_connection(cls, connected_obj, index):
        return connected_obj.GetSrcObject(index)

    # @classmethod
    # def _fbx_connect(cls, connected_obj, fbx_object):
    #     res = connected_obj.ConnectSrcObject(fbx_object)
    #     return res
    #
    # def _disconnect_indices(self, indices):
    #     return bfFbxUtils.BfDisconnectIndices.src_objects(self.connected_obj(), indices)

    def _fbx_disconnect_all(self):
        """Override method to disconnect all source objects
        """
        res = self.connected_obj().DisconnectAllSrcObject()
        return res


class BfFbxDstObjectsManager(BfFbxObjectConnectionsManager):
    ROOT_ITEM_CLS = BfDstObjectsRootItem

    def __init__(self, *args, **kwargs):
        super(BfFbxDstObjectsManager, self).__init__(*args, **kwargs)

    @classmethod
    def get_connection_count(cls, connected_obj):
        return connected_obj.GetDstObjectCount()

    @classmethod
    def get_connection(cls, connected_obj, index):
        return connected_obj.GetDstObject(index)

    #
    # @classmethod
    # def _fbx_connect(cls, connected_obj, fbx_object):
    #     res = connected_obj.ConnectDstObject(fbx_object)
    #     return res
    #
    # def _disconnect_indices(self, indices):
    #     return bfFbxUtils.BfDisconnectIndices.dst_objects(self.connected_obj(), indices)

    def _fbx_disconnect_all(self):
        """Override method to disconnect all source objects
        """
        res = self.connected_obj().DisconnectAllDstObject()
        return res


class BfFbxSrcPropertiesManager(BfFbxPropertyConnectionsManager):
    ROOT_ITEM_CLS = BfSrcPropertiesRootItem

    def __init__(self, *args, **kwargs):
        super(BfFbxSrcPropertiesManager, self).__init__(*args, **kwargs)

    @classmethod
    def get_connection_count(cls, connected_obj):
        data = connected_obj.GetSrcPropertyCount()
        print "PROP COUNT", connected_obj.GetName(), data
        return data

    @classmethod
    def get_connection(cls, connected_obj, index):
        return connected_obj.GetSrcProperty(index)

    # @classmethod
    # def _fbx_connect(cls, connected_obj, fbx_property):
    #     res = connected_obj.ConnectSrcProperty(fbx_property)
    #     return res
    #
    # def _disconnect_indices(self, indices):
    #     return bfFbxUtils.BfDisconnectIndices.src_properties(self.connected_obj(), indices)

    def _fbx_disconnect_all(self):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res


class BfFbxDstPropertiesManager(BfFbxPropertyConnectionsManager):
    ROOT_ITEM_CLS = BfDstPropertiesRootItem

    def __init__(self, *args, **kwargs):
        super(BfFbxDstPropertiesManager, self).__init__(*args, **kwargs)

    @classmethod
    def get_connection_count(cls, connected_obj):
        return connected_obj.GetDstPropertyCount()

    @classmethod
    def get_connection(cls, connected_obj, index):
        return connected_obj.GetDstProperty(index)

    # @classmethod
    # def _fbx_connect(cls, connected_obj,  fbx_property):
    #     res = connected_obj.ConnectDstProperty(fbx_property)
    #     return res
    #
    # def _disconnect_indices(self, indices):
    #     return bfFbxUtils.BfDisconnectIndices.dst_properties(self.connected_obj(), indices)

    def _fbx_disconnect_all(self):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res

class Test1(object):
    def __init__(self, base):
        fbx_object = base._scene.GetRootNode()

        item_manager = BfFbxSrcObjectsManager(bf_app=base.bf_environment())
        item_manager.set_debug_level(item_manager.LEVELS.all())
        item_manager.set_connected_obj(fbx_object)

        item_manager.debug_hierarchy()


if __name__ == "__main__":
    import os

    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"

    from brenfbx.utils import bfEnvironmentUtils

    base = brenfbx.test.bfTestBase.BfTestBase(
        file_path=os.path.join(DUMP_DIR, TEST_FILE),
        use_custom_objects=False,
        use_qt=False
    )

    test = Test1(base)
