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
    bfFilterSettings, bfPropertyModels, bfQtCore, bfSceneQtCache, bfConnectionProxyModels
from brenfbx.qt import bfPropertyQtCache


# base models ---
class BFbxConnectionModelBase(Qt.QtCore.QAbstractItemModel):
    """
    """

    kFbxClassRole = Qt.QtCore.Qt.UserRole

    def __init__(self, parent=None):
        super(BFbxConnectionModelBase, self).__init__(parent=parent)

        self._connected_model = None

#         if connected_model is not None:
#             self.set_connected_model(connected_model)

    def scene_cache(self):
        if self.scene_model() is None:
            return None

        return self.scene_model().scene_cache()

    def scene_model(self):
        return self._connected_model.scene_model()

    def connected_model(self):
        return self._connected_model

    def set_connected_model(self, connected_model):
        """TODO checks
        TODO connect signals
        """
        self.beginResetModel()
        self._connected_model = connected_model
        self.endResetModel()

    def property_model(self):
        if self.scene_model() is None:
            return None

        return self._connected_model.property_model()

    def _row_count(self, index):
        return 0

    def rowCount(self, index):
        if self.connected_model() is None:
            return 0

        if not index.isValid():
            # connected level
            # get rowCount of connected proxy model
            return self._connected_model.rowCount(Qt.QtCore.QModelIndex())
        else:
            if self.scene_model().is_dummy(index):
                return 0

            # connection level
            # get rowCount from subclass depending on
            # type of connection
            return self._row_count(index)

    def _column_count(self, index):
        return 0

    def columnCount(self, index):
        if self.scene_model() is None:
            return 0

        return self._column_count(index)

    def _header_data(self, section, orientation, role):
        return None

    def headerData(self, section, orientation, role):
        if self.scene_model() is None:
            return None

        return self._header_data(
            section, orientation, role
        )

    def flags(self, index):
        """ hard-coded item flags
        For now lets keep stuff non-editable
        """
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def setData(self, index, value):
        return False

    def index(self, row, column, parent_index):
        if not parent_index.isValid():
            # root level
            connected_index = self._connected_model.index(
                row, column, Qt.QtCore.QModelIndex()
            )

#             data = self._connected_model.get_id_object(
#                 connected_index
#             )
            data = connected_index.internalPointer()

        else:
            # connection level
            connected_index = self._connected_model.index(
                parent_index.row(), column, Qt.QtCore.QModelIndex()
            )

            data = self._connected_model.get_id_con_object(
                connected_index
            )

        index = self.createIndex(
            row, column, data
        )

        return index

    def parent(self, index):
        data = index.internalPointer()

        if isinstance(
            data,
            (
                bfSceneQtCache.BfIdConData,
                bfPropertyQtCache.BfPropertyConId
            )
        ):
            # connection level
            # get parent row
            parent_row = self._connected_model.find_row(data.value())

            parent_data = self._connected_model.get_id_object(
                data.value()
            )

            parent_index = self.createIndex(
                parent_row, 0, parent_data
            )

            return parent_index

        elif isinstance(
            data,
            (
                bfSceneQtCache.BfIdData,
                bfSceneQtCache.BfIdDummyData,
                bfPropertyQtCache.BfPropertyId,
            )
        ):
            # connected level
            # return invalid index to indicate root level
            return Qt.QtCore.QModelIndex()

        else:
            raise bfQtCore.BfQtError(
                "Failed to create parent index: {} {}".format(index, data)
            )

    def remove_rows(self, index, rows):
        """Disconnect specified row indices
        """

        values = [self.get_connection(index, row) for row in rows]

        for value in values:
            self.fbx_disconnect(index, value)

        return True

    def removeIndices(self, indices):
        """
        TODO
        """
        if self.scene_model() is None:
            return False

        if not len(indices):
            return False

        # TODO check indices all have same parent
        parent_index = indices[0].Parent()

        rows = [i.row() for i in indices]

        self.beginResetModel()

        res = self.remove_rows(parent_index, rows)

        self.endResetModel()

        return res

    def get_id_value(self, value):
        data = value.internalPointer()
        return data.value()

    def get_connected(self, index):
        """Get connected object/property from connected model 
        """
#         id_value = self.get_id_value(index)
        return self._connected_model.get_connected(index)

    def _get_connection(self, index, row):
        """Overridable method to get srs/dst object/property connection 
        """
        return None

    def get_connection(self, index, row):
        """Get srs/dst object/property connection 
        """
        if self.get_connected(index) is None:
            return None

        return self._get_connection(index, row)

    def _connect(self, index, value):
        """Overridable method to create new connection
        """
        pass

    def fbx_connect(self, index, value):
        """Create new connection
        """
        if self.get_connected(index) is None:
            return False

        self.beginResetModel()

        res = self._connect(index, value)

        self.endResetModel()

        return res

    def _disconnect(self, index, value):
        """Overridable method to disconnect source object/property
        """
        pass

    def fbx_disconnect(self, index, value):
        """Disconnect source object/property
        """
        if self.get_connected(index) is None:
            return False

        self.beginResetModel()

        res = self._disconnect(index, value)

        self.endResetModel()

        return res

    def _disconnect_all(self, index):
        """Overridable method to disconnect all source objects/properties
        """
        pass

    def fbx_disconnect_all(self, index):
        """Disconnect all source objects/properties
        """
        if self.get_connected(index) is None:
            return False

        self.beginResetModel()

        res = self._disconnect_all(index)

        self.endResetModel()

        return res


class BFbxObjectConnectionModelBase(BFbxConnectionModelBase):
    """
    """

    def __init__(self, parent=None):
        super(BFbxObjectConnectionModelBase, self).__init__(
            parent=parent
        )

    def _column_count(self, index):

        return self.scene_model().columnCount(index)

    def _header_data(self, section, orientation, role):

        return self.scene_model().headerData(
            section, orientation, role
        )

    def data(self, index, role):
        """
        """
        if self.scene_model() is None:
            return None

        if not index.isValid():
            return

        if not index.parent().isValid():
            # root level
            data = self._connected_model.data(
                index, role
            )

            return data
        else:
            # connection level
            row = index.row()
            column = index.column()

            if row > self.rowCount(None):
                return Qt.QtCore.QModelIndex()

            con_object = self.get_connection(index, row)

            con_object_id = con_object.GetUniqueID()

            data = self._scene_model.get_fbx_object_data(
                con_object_id, column, role
            )

        return data


class BFbxPropertyConnectionModelBase(BFbxConnectionModelBase):
    """Base class for model looking for a connected property.
    """

    def __init__(self, parent=None):
        super(BFbxPropertyConnectionModelBase, self).__init__(
            parent=parent
        )

    def _column_count(self, index):

        return self.property_model().columnCount()

    def _header_data(self, section, orientation, role):

        return self.property_model().headerData(
            section, orientation, role
        )

    def data(self, index, role):
        """
        TODO more checks and helper methods
        """

        # check index is valid
        if not index.isValid():
            return

        if not index.parent().isValid():

            data = self._connected_model.data(
                index, role
            )

            return data

        else:
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

        return None


class BFbxSrcObjectModel(BFbxObjectConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxSrcObjectModel, self).__init__(
            parent=parent
        )

    def _row_count(self, index):
        return self.get_connected(index).GetSrcObjectCount()

    def _get_connection(self, index, row):
        """Override method to return connected object
        """
        fbx_object = self.get_connected(index)
        src_object = fbx_object.GetSrcObject(row)

        return src_object

    def _connect(self, index, fbx_object):
        res = self.get_connected(index).ConnectSrcObject(fbx_object)
        return res

    def _disconnect(self, index, fbx_object):
        res = self.get_connected(index).DisconnectSrcObject(fbx_object)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects
        """
        res = self.get_connected().DisconnectAllSrcObject()
        return res


class BFbxDstObjectModel(BFbxObjectConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxDstObjectModel, self).__init__(
            parent=parent
        )

    def _row_count(self, index):
        return self.get_connected(index).GetDstObjectCount()

    def _get_connection(self, index, row):
        """Override method to return connected object
        """
        fbx_object = self.get_connected(index)
        src_object = fbx_object.GetDstObject(row)

        return src_object

    def _connect(self, index, fbx_object):
        res = self.get_connected(index).ConnectDstObject(fbx_object)
        return res

    def _disconnect(self, index, fbx_object):
        res = self.get_connected(index).DisconnectDstObject(fbx_object)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects
        """
        res = self.get_connected().DisconnectAllDstObject()
        return res


class BFbxSrcPropertyModel(BFbxPropertyConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxSrcPropertyModel, self).__init__(
            parent=parent
        )

    def _row_count(self, index):
        return self.get_connected(index).GetSrcPropertyCount()

    def _get_connection(self, index, row):
        """Override method to return connected property
        """
        src_property = self.get_connected(index).GetSrcProperty(row)
        return src_property

    def _connect(self, index, fbx_property):
        res = self.get_connected(index).ConnectSrcProperty(fbx_property)
        return res

    def _disconnect(self, index, fbx_property):
        res = self.get_connected(index).DisconnectSrcProperty(fbx_property)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res


class BFbxDstPropertyModel(BFbxPropertyConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxDstPropertyModel, self).__init__(
            parent=parent
        )

    def _row_count(self, index):
        return self.get_connected(index).GetDstPropertyCount()

    def _get_connection(self, index, row):
        """Override method to return connected property
        """
        src_property = self.get_connected(index).GetDstProperty(row)
        return src_property

    def _connect(self, index, fbx_property):
        res = self.get_connected(index).ConnectDstProperty(fbx_property)
        return res

    def _disconnect(self, index, fbx_property):
        res = self.get_connected(index).DisconnectDstProperty(fbx_property)
        return res

    def _disconnect_all(self):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res


class BfConnectionModelManager(object):
    def __init__(self):
        super(BfConnectionModelManager, self).__init__()

        self._scene_model = None

#         self._connected_object_model = bfConnectionProxyModels.BfConnectedObjectProxyModel()
        self._connected_property_model = bfConnectionProxyModels.BfConnectedPropertyProxyModel()

#         self._src_oo_model = BFbxSrcObjectModel()
        self._src_op_model = BFbxSrcObjectModel()
#
#         self._dst_oo_model = BFbxDstObjectModel()
#         self._dst_op_model = BFbxDstObjectModel()

#         self._src_po_model = BFbxSrcPropertyModel()
#         self._src_pp_model = BFbxSrcPropertyModel()
#
#         self._dst_po_model = BFbxDstPropertyModel()
#         self._dst_pp_model = BFbxDstPropertyModel()

        for model in [
            #             self._src_oo_model,
            #             self._src_po_model,
            #             self._dst_oo_model,
            #             self._dst_po_model,
        ]:
            model.set_connected_model(
                #                 self._connected_object_model
            )

        for model in [
            self._src_op_model,
            #             self._src_pp_model,
            #             self._dst_op_model,
            #             self._dst_pp_model,
        ]:
            model.set_connected_model(
                self._connected_property_model
            )

    def set_scene_model(self, scene_model):
        self._scene_model = scene_model

#         self._connected_object_model.setSourceModel(scene_model)
        self._connected_property_model.setSourceModel(scene_model)

    def src_oo_model(self):
        """Return source object-object connection model.
        """
        return self._src_oo_model

    def src_op_model(self):
        """Return source object-property connection model.
        """
        return self._src_op_model

    def src_po_model(self):
        """Return source property-object connection model.
        """
        return self._src_po_model

    def src_pp_model(self):
        """Return source property-property connection model.
        """
        return self._src_pp_model

    def dst_oo_model(self):
        """Return destination object-object connection model.
        """
        return self._dst_oo_model

    def dst_op_model(self):
        """Return destination object-property connection model.
        """
        return self._dst_op_model

    def dst_po_model(self):
        """Return destination property-object connection model.
        """
        return self._dst_po_model

    def dst_pp_model(self):
        """Return destination property-property connection model.
        """
        return self._dst_pp_model
