"""
TODO

Qt models to represent connections between fbx objects and properties.

For now we're only dealing with Src connections.

"""

import sys

import os
import fbx
import FbxCommon
import inspect
from types import NoneType

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

from brenpy.cg import bpEuler
from brenpy.utils import bpStr
from brenpy.qt import bpQtCore
from brenpy.qt import bpQtWidgets
from brenpy.qt.icons import icons8

from brenfbx.core import bfIO
from brenfbx.core import bfUtils
from brenfbx.core import bfCore
from brenfbx.core import bfProperty
from brenfbx.core import bfObject

from brenfbx.qt import bfQtWidgets, bfSceneMenus, bfSceneModels, bfDataModels,\
    bfFilterSettings, bfPropertyModels, bfQtCore
from brenfbx.qt import bfPropertyQtCache


# base models ---
class BFbxConnectionModelBase(Qt.QtCore.QAbstractTableModel):
    """
    """

    kFbxClassRole = Qt.QtCore.Qt.UserRole

    def __init__(self, scene_model=None, parent=None):
        super(BFbxConnectionModelBase, self).__init__(parent=parent)

        self._scene_model = None

        if scene_model is not None:
            self.set_scene_model(scene_model)

    def scene_cache(self):
        if self._scene_model is None:
            return None

        return self._scene_model.scene_cache()

    def scene_model(self):
        return self._scene_model

    def set_scene_model(self, scene_model):
        self.beginResetModel()
        self._scene_model = scene_model
        self.endResetModel()

    def property_model(self):
        if self._scene_model is None:
            return None

        return self._scene_model.property_model()

    def _row_count(self, index):
        return 0

    def rowCount(self, index):
        if self.get_connected() is None:
            return 0

        return self._row_count(index)

    def columnCount(self, index):
        if self._scene_model is None:
            return 0

        return self._scene_model.columnCount()

    def headerData(self, section, orientation, role):
        if self._scene_model is None:
            return None

        return self._scene_model.headerData(
            section, orientation, role
        )

    def flags(self, index):
        """ hard-coded item flags """
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def setData(self, value):
        return False

    def remove_rows(self, rows):
        """Disconnect specified row indices
        """

        values = [self.get_connection(row) for row in rows]

        for value in values:
            self.fbx_disconnect(value)

        return True

    def removeIndices(self, indices):
        """
        TODO
        """
        if self._scene_model is None:
            return False

        if not len(indices):
            return False

        rows = [i.row() for i in indices]

        self.beginResetModel()

        res = self.remove_rows(rows)

        self.endResetModel()

        return res

    def get_connected(self):
        """Overridable method to get connected object/property 
        """
        pass

    def _get_connection(self, row):
        """Overridable method to get srs/dst object/property connection 
        """
        return None

    def get_connection(self, row):
        """Get srs/dst object/property connection 
        """
        if self.get_connected() is None:
            return None

        return self._get_connection(row)

    def _connect(self, value):
        """Overridable method to create new connection
        """
        pass

    def fbx_connect(self, value):
        """Create new connection
        """
        if self.get_connected() is None:
            return False

        self.beginResetModel()

        res = self._connect(value)

        self.endResetModel()

        return res

    def _disconnect(self, value):
        """Overridable method to disconnect source object/property
        """
        pass

    def fbx_disconnect(self, value):
        """Disconnect source object/property
        """
        if self.get_connected() is None:
            return False

        self.beginResetModel()

        res = self._disconnect(value)

        self.endResetModel()

        return res

    def _disconnect_all(self):
        """Overridable method to disconnect all source objects/properties
        """
        pass

    def fbx_disconnect_all(self):
        """Disconnect all source objects/properties
        """
        if self.get_connected() is None:
            return False

        self.beginResetModel()

        res = self._disconnect_all()

        self.endResetModel()

        return res


class BFbxObjectConnectionModelBase(BFbxConnectionModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxObjectConnectionModelBase, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def data(self, index, role):
        """
        """
        if self._scene_model is None:
            return None

        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        if row > self.rowCount(None):
            return Qt.QtCore.QModelIndex()

        con_object = self.get_connection(row)

        con_object_id = con_object.GetUniqueID()

        data = self._scene_model.get_fbx_object_data(
            con_object_id, column, role
        )

        return data


class BFbxPropertyConnectionModelBase(BFbxConnectionModelBase):
    """Base class for model looking for a connected property.
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxPropertyConnectionModelBase, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def data(self, index, role):
        """
        TODO more checks and helper methods
        """

        # check index is valid
        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        if row > self.rowCount(None):
            return Qt.QtCore.QModelIndex()

        # get connected property objects
        con_property = self.get_connection(row)

        if con_property is None:
            raise bfQtCore.BfQtError(
                "Failed to get connected FbxProperty"
            )

        con_property_id = bfUtils.get_fbx_property_object_index(
            con_property
        )

        con_object = con_property.GetFbxObject()
        con_object_id = con_object.GetUniqueID()

        con_property_cache = self.scene_cache().get_property_cache(
            con_object_id
        )

        if con_property_cache is None:
            raise bfQtCore.BfQtError(
                "Failed to find cache for connected Property"
            )

        con_property_item = con_property_cache.get_item_from_unique_id(
            con_property_id
        )

        if con_property_item is None:
            raise bfQtCore.BfQtError(
                "Failed to find item for connected Property"
            )

        # get connected property data
        if column == 0:
            con_object_data = self._scene_model.get_fbx_object_data(
                con_object_id, column, role
            )

            if role in [Qt.QtCore.Qt.DisplayRole]:
                # append property name
                con_property_data = self._scene_model.property_model()._get_prop_fn_data(
                    column, role, con_property_item
                )

                data = "{}.{}".format(
                    con_object_data, con_property_data
                )

                return data
            else:
                return con_object_data

        else:
            con_property_data = self._scene_model.property_model()._get_prop_fn_data(
                column, role, con_property_item
            )

            return con_property_data

        return data


class BFbxSrcObjectModelBase(BFbxObjectConnectionModelBase):

    def __init__(self, scene_model=None, parent=None):
        super(BFbxSrcObjectModelBase, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def _row_count(self, index):
        return self.get_connected().GetSrcObjectCount()

    def _get_connection(self, row):
        """Override method to return connected object
        """
        fbx_object = self.get_connected()
        src_object = fbx_object.GetSrcObject(row)

        return src_object

    def _connect(self, fbx_object):
        res = self.get_connected().ConnectSrcObject(fbx_object)
        return res

    def _disconnect(self, fbx_object):
        res = self.get_connected().DisconnectSrcObject(fbx_object)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects
        """
        res = self.get_connected().DisconnectAllSrcObject()
        return res


class BFbxDstObjectModelBase(BFbxObjectConnectionModelBase):

    def __init__(self, scene_model=None, parent=None):
        super(BFbxDstObjectModelBase, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def _row_count(self, index):
        return self.get_connected().GetDstObjectCount()

    def _get_connection(self, row):
        """Override method to return connected object
        """
        fbx_object = self.get_connected()
        src_object = fbx_object.GetDstObject(row)

        return src_object

    def _connect(self, fbx_object):
        res = self.get_connected().ConnectDstObject(fbx_object)
        return res

    def _disconnect(self, fbx_object):
        res = self.get_connected().DisconnectDstObject(fbx_object)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects
        """
        res = self.get_connected().DisconnectAllDstObject()
        return res


class BFbxSrcPropertyModelBase(BFbxPropertyConnectionModelBase):

    def __init__(self, scene_model=None, parent=None):
        super(BFbxSrcPropertyModelBase, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def _row_count(self, index):
        return self.get_connected().GetSrcPropertyCount()

    def _get_connection(self, row):
        """Override method to return connected property
        """
        src_property = self.get_connected().GetSrcProperty(row)
        return src_property

    def _connect(self, fbx_property):
        res = self.get_connected().ConnectSrcProperty(fbx_property)
        return res

    def _disconnect(self, fbx_property):
        res = self.get_connected().DisconnectSrcProperty(fbx_property)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res


class BFbxDstPropertyModelBase(BFbxPropertyConnectionModelBase):

    def __init__(self, scene_model=None, parent=None):
        super(BFbxDstPropertyModelBase, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def _row_count(self, index):
        return self.get_connected().GetDstPropertyCount()

    def _get_connection(self, row):
        """Override method to return connected property
        """
        src_property = self.get_connected().GetDstProperty(row)
        return src_property

    def _connect(self, fbx_property):
        res = self.get_connected().ConnectDstProperty(fbx_property)
        return res

    def _disconnect(self, fbx_property):
        res = self.get_connected().DisconnectDstProperty(fbx_property)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res

# connected object models ---


class BFbxSrcPOModel(BFbxSrcPropertyModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxSrcPOModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def set_object_id(self, object_id):
        self._object_id = object_id

    def get_connected(self):
        return self._scene_model.get_fbx_object(
            self._object_id
        )


class BFbxDstPOModel(BFbxDstPropertyModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxDstPOModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def set_object_id(self, object_id):
        self._object_id = object_id

    def get_connected(self):
        return self._scene_model.get_fbx_object(
            self._object_id
        )


class BFbxSrcOOModel(BFbxSrcObjectModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxSrcOOModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

        self._object_id = None

    def set_object_id(self, object_id):
        self._object_id = object_id

    def get_connected(self):
        return self._scene_model.get_fbx_object(
            self._object_id
        )


class BFbxDstOOModel(BFbxDstObjectModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxDstOOModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

        self._object_id = None

    def set_object_id(self, object_id):
        self._object_id = object_id

    def get_connected(self):
        return self._scene_model.get_fbx_object(
            self._object_id
        )


# connected property models ---


class BFbxSrcOPModel(BFbxSrcObjectModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxSrcOPModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

        self._property_item = None

    def set_property(self, object_id, property_id):
        self.beginResetModel()

        property_cache = self.scene_cache().get_property_cache(object_id)

        self._property_item = property_cache.get_item_from_unique_id(
            property_id)

        self.endResetModel()

    def get_connected(self):
        if self._property_item == None:
            return None

        return self._property_item.property_object().Property()


class BFbxDstOPModel(BFbxDstObjectModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxDstOPModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

        self._property_item = None

    def set_property(self, object_id, property_id):

        property_cache = self.scene_cache().get_property_cache(object_id)

        self._property_item = property_cache.get_item_from_unique_id(
            property_id)

    def get_connected(self):
        return self._property_item.property_object().Property()


class BFbxSrcPPModel(BFbxSrcPropertyModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxSrcPPModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

        self._property_item = None

    def set_property(self, object_id, property_id):
        self.beginResetModel()

        print "DEBUG", object_id, property_id
        self._property_cache = self.scene_cache().get_property_cache(object_id)

        self._property_item = self._property_cache.get_item_from_unique_id(
            property_id)

        print "DEBUG", self._property_cache, self._property_item

#         self._property_model = self._scene_model.get_property_model(
#             object_id
#         )
        self.endResetModel()

    def get_connected(self):
        if self._property_item is None:
            return None

        return self._property_item.property_object().Property()


class BFbxDstPPModel(BFbxDstPropertyModelBase):
    """
    """

    def __init__(self, scene_model=None, parent=None):
        super(BFbxDstPPModel, self).__init__(
            scene_model=scene_model, parent=parent
        )

    def set_property(self, object_id, property_id):

        self._property_cache = self.scene_cache().get_property_cache(object_id)

        self._property_item = self._property_cache.get_item_from_unique_id(
            property_id)

#         self._property_model = self._scene_model.get_property_model(
#             object_id
#         )

    def get_connected(self):
        return self._property_item.property_object().Property()
