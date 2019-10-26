"""Qt models to represent connections between fbx objects and properties.

** WIP **

Connection models do no need their own caches, as fbxConnections do not have
their own classes to cache.

Instead we can use the scene and property models as source models,
convert these to flat lists models, and add connections as child items.

When retrieving a connection, first we determine if we are at root level,
if so we can find the connected object/property via the source models.

If we are connection level, when creating the index, we should store a pointer
to the id of the connected object/property so we know which object to query
connections for.

In both cases we can create a proxy index which points to the source index
pointer.

TODO actually do we even need a proxy index?!?!



TODO does it even need to be a proxy model!?!?!

- Answer:
    yeah kinda, initial attempts at using a tree model with reference
    to proxy model getting convoluted, especially when mixing models.
    
    A better solution may be to use proxy model, and querying connection data
    directly from fbx objects (but keeping the data simple, like names only).
    
    Then connencting scene models and property models data changed signals,
    to all the proxy models for safety.
    
    Indexes should still store id objects, that way when selecting a connection
    we are still able to find indexes in other models.

    This also means we need to use multiple-inheritance, for our connection
    query methods.

When querying data we ask if we are at root level or child level,
to know if we are querying connection or connected.

TODO should we store our own item to list model?

** SUPER WIP **


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

from brenfbx.qt import bfSceneMenus, bfSceneModels, bfDataModels,\
    bfFilterSettings, bfPropertyModels, bfQtCore, bfSceneQtCache

from brenfbx.qt import bfPropertyQtCache


class BfConnectedProxyModelBase(bpQtCore.BpItemToListProxyModel):
    def __init__(self, parent=None):
        super(BfConnectedProxyModelBase, self).__init__(
            parent=parent
        )

        self._connection_model = None

        self._parity_models = bpQtCore.BpParityModels()

    def setSourceModel(self, source_model):
        super(
            BfConnectedProxyModelBase, self
        ).setSourceModel(source_model)

    def set_connection_model(self, connection_model):
        """TODO checks depending on subclass?
        """
        self._connection_model = connection_model

    def connection_model(self):
        """Model that we query data from regarding src/dst connection
        """
        return self._connection_model

#     def scene_model(self):
#         if isinstance(self.get_root_model(), bfPropertyModels.BFbxPropertyModel):
#             return self.get_root_model().scene_model()
#
#         elif isinstance(self.get_root_model(), bfSceneModels.BFbxSceneTreeQtModel):
#             return self.get_root_model()
#
#         else:
#             raise bfQtCore.BfQtError(
#                 "Failed to retreive scene model: {}".format(
#                     self.get_root_model()
#                 )
#             )

    def add_parity_model(self, model):
        self._parity_models.add_model(model)
#
#     def scene_cache(self):
#         return self.scene_model().scene_cache()

#     def property_model(self):
#         if isinstance(self.get_root_model(), bfPropertyModels.BFbxPropertyModel):
#             return self.get_root_model()
#
#         elif isinstance(self.get_root_model(), bfSceneModels.BFbxSceneTreeQtModel):
#             return self.get_root_model().property_model()
#
#         else:
#             raise bfQtCore.BfQtError(
#                 "Failed to retreive property model: {}".format(
#                     self.get_root_model()
#                 )
#             )
#
#     def get_property_cache(self, index):
#         """TODO if neccessary"""
#         pass

    def get_connected(self, proxy_index):
        if self.sourceModel() is None:
            raise bfQtCore.BfQtError(
                "Cannot retreive connected object or property when sourceModel is None"
            )

        #         source_index = self.map_to_root(proxy_index)

        if isinstance(self.get_root_model(), bfPropertyModels.BFbxPropertyModel):
            fbx_property = self.get_root_model().get_fbx_property(proxy_index)
            return fbx_property

        elif isinstance(self.get_root_model(), bfSceneModels.BFbxSceneTreeQtModel):
            fbx_object = self.get_root_model().get_fbx_object(proxy_index)
            return fbx_object

        else:
            raise bfQtCore.BfQtError(
                "Failed to retreive connected object or property: {}".format(
                    proxy_index
                )
            )

    def _connection_count(self, parent_index):
        """Overidable method
        """
        return 0

    def columnCount(self, index):
        """To keep things simple, we should only display names"""
        return 1

    def rowCount(self, parent_index):
        if parent_index.isValid():

            if isinstance(
                parent_index.internalPointer(), bpQtCore.IndexPath
            ):
                # connections do not have any children of their own
                row_count = 0

            elif isinstance(
                parent_index.internalPointer(),
                (
                    bfPropertyQtCache.BfPropertyId,
                    bfSceneQtCache.BfIdData,
                    bfSceneQtCache.BfIdDummyData
                )
            ):
                # connection level
                row_count = self._connection_count(parent_index)
                return row_count
            else:
                raise bfQtCore.BfQtError(
                    "Unrecognised valid parent index, cannot get row count: {} {}".format(
                        parent_index, parent_index.internalPointer()
                    )
                )

# print "row count {} {}".format(row_count,
# parent_index.internalPointer())

        else:
            # root level
            row_count = super(
                BfConnectedProxyModelBase, self
            ).rowCount(parent_index)

        return row_count

#         else:
#             raise bfQtCore.BfQtError(
#                 "Unrecognised invalid parent index, cannot get row count: {} {}".format(
#                     parent_index, parent_index.internalPointer()
#                 )
#             )

    def hasChildren(self, parent_index):
        """Inform Qt of new children.

        Note:
            This method overide is CRUCIAL!
            Otherwise new children would not be shown!

        """
        return self.rowCount(parent_index) > 0

    def index(self, row, column, parent_index):
        """
        TODO check this is using correct path for src PP models!
        """
        if parent_index.isValid():
            if isinstance(parent_index.internalPointer(), bpQtCore.IndexPath):
                return Qt.QtCore.QModelIndex()
#                 raise bfQtCore.BfQtError(
#                     "Cannot create child index for connection index."
#                 )

            # store path object to trace back to parent
            parent_path = bpQtCore.IndexPath(parent_index)

            cached_source_path = self._proxy_to_source_map[parent_path.key()]

            cached_proxy_path = self._source_to_proxy_map[
                cached_source_path.key()
            ]

            index = self.createIndex(row, column, cached_proxy_path)
            return index

        else:
            # normal behaviour
            return super(BfConnectedProxyModelBase, self).index(row, column, parent_index)

    def parent(self, index):
        data = index.internalPointer()

        if isinstance(data, bpQtCore.IndexPath):
            # get cached parent proxy index
            #             cached_parent_proxy_path = data
            parent_proxy_index = data.get(self)

            return parent_proxy_index

        else:
            # otherwise root level
            return Qt.QtCore.QModelIndex()

    def flags(self, index):
        """ hard-coded item flags
        For now lets keep stuff non-editable
        """
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def setData(self, index, value):
        return False

    def data(self, index, role):
        if role in [Qt.QtCore.Qt.DisplayRole]:
            role = self.get_root_model().kPathNameStrRole

        return super(BfConnectedProxyModelBase, self).data(
            index, role
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
        if self.sourceModel() is None:
            return False

        if not len(indices):
            return False

        # TODO check indices all have same parent
        parent_index = indices[0].parent()

        rows = [i.row() for i in indices]

        self.beginResetModel()

        res = self.remove_rows(parent_index, rows)

        self.endResetModel()

        return res

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

    def _fbx_connect(self, index, value):
        """Overridable method to create new connection
        """
        pass

    def fbx_connect(self, index, value):
        """Create new connection
        """
        if self.get_connected(index) is None:
            return False

        self.beginResetModel()
        self._parity_models.beginResetModels()

        res = self._fbx_connect(index, value)

        self.endResetModel()
        self._parity_models.endResetModels()

        return res

    def _fbx_disconnect(self, index, value):
        """Overridable method to disconnect source object/property
        """
        pass

    def fbx_disconnect(self, index, value):
        """Disconnect source object/property
        """
        if self.get_connected(index) is None:
            return False

        self.beginResetModel()
        self._parity_models.beginResetModels()

        res = self._fbx_disconnect(index, value)

        self.endResetModel()
        self._parity_models.endResetModels()

        return res

    def _fbx_disconnect_all(self, index):
        """Overridable method to disconnect all source objects/properties
        """
        pass

    def fbx_disconnect_all(self, index):
        """Disconnect all source objects/properties
        """
        if self.get_connected(index) is None:
            return False

        self.beginResetModel()
        self._parity_models.beginResetModels()

        res = self._fbx_disconnect_all(index)

        self.endResetModel()
        self._parity_models.endResetModels()

        return res


class BFbxObjectConnectionModelBase(BfConnectedProxyModelBase):
    """
    """

    def __init__(self, parent=None):
        super(BFbxObjectConnectionModelBase, self).__init__(
            parent=parent
        )

    def data(self, index, role):
        """
        """
        if self.sourceModel() is None:
            return None

        if not index.isValid():
            return

        if not index.parent().isValid():
            # root level
            return super(BFbxObjectConnectionModelBase, self).data(index, role)

        else:
            # connection level
            row = index.row()
            column = index.column()

            if row > self.rowCount(Qt.QtCore.QModelIndex()):
                return Qt.QtCore.QModelIndex()

            con_object = self.get_connection(index.parent(), row)

            if role in [Qt.QtCore.Qt.DisplayRole]:
                return str(con_object.GetName())

        return None


class BFbxPropertyConnectionModelBase(BfConnectedProxyModelBase):
    """Base class for model looking for a connected property.
    """

    def __init__(self, parent=None):
        super(BFbxPropertyConnectionModelBase, self).__init__(
            parent=parent
        )

    def data(self, index, role):
        """
        TODO more checks and helper methods
        """
        if self.sourceModel() is None:
            return None

        # check index is valid
        if not index.isValid():
            return

        if not index.parent().isValid():
            # root level
            return super(BFbxPropertyConnectionModelBase, self).data(index, role)

        else:
            # connection level
            row = index.row()
            column = index.column()

#             if row > self.rowCount(Qt.QtCore.QModelIndex()):
#                 return Qt.QtCore.QModelIndex()

            con_property = self.get_connection(index.parent(), row)

            if role in [Qt.QtCore.Qt.DisplayRole]:
                return "{}.{}".format(
                    con_property.GetFbxObject().GetName(),
                    con_property.GetName()
                )

        return None


class BFbxSrcObjectModel(BFbxObjectConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxSrcObjectModel, self).__init__(
            parent=parent
        )

    def _connection_count(self, index):
        return self.get_connected(index).GetSrcObjectCount()

    def _get_connection(self, index, row):
        """Override method to return connected object
        """
        fbx_object = self.get_connected(index)
        src_object = fbx_object.GetSrcObject(row)

        return src_object

    def _fbx_connect(self, index, fbx_object):
        res = self.get_connected(index).ConnectSrcObject(fbx_object)
        return res

    def _fbx_disconnect(self, index, fbx_object):
        res = self.get_connected(index).DisconnectSrcObject(fbx_object)
        return res

    def _fbx_disconnect_all(self, index):
        """Override method to disconnect all source objects
        """
        res = self.get_connected(index).DisconnectAllSrcObject()
        return res


class BFbxDstObjectModel(BFbxObjectConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxDstObjectModel, self).__init__(
            parent=parent
        )

    def _connection_count(self, index):
        return self.get_connected(index).GetDstObjectCount()

    def _get_connection(self, index, row):
        """Override method to return connected object
        """
        fbx_object = self.get_connected(index)
        src_object = fbx_object.GetDstObject(row)

        return src_object

    def _fbx_connect(self, index, fbx_object):
        res = self.get_connected(index).ConnectDstObject(fbx_object)
        return res

    def _fbx_disconnect(self, index, fbx_object):
        res = self.get_connected(index).DisconnectDstObject(fbx_object)
        return res

    def _fbx_disconnect_all(self, index):
        """Override method to disconnect all source objects
        """
        res = self.get_connected(index).DisconnectAllDstObject()
        return res


class BFbxSrcPropertyModel(BFbxPropertyConnectionModelBase):

    def __init__(self, parent=None):
        super(BFbxSrcPropertyModel, self).__init__(
            parent=parent
        )

    def _connection_count(self, index):
        prop = self.get_connected(index)
        con_count = prop.GetSrcPropertyCount()
        return con_count

    def _get_connection(self, index, row):
        """Override method to return connected property
        """
        src_property = self.get_connected(index).GetSrcProperty(row)
        return src_property

    def _fbx_connect(self, index, fbx_property):
        res = self.get_connected(index).ConnectSrcProperty(fbx_property)
        return res

    def _fbx_disconnect(self, index, fbx_property):
        res = self.get_connected(index).DisconnectSrcProperty(fbx_property)
        return res

    def _fbx_disconnect_all(self, index):
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

    def _connection_count(self, index):
        return self.get_connected(index).GetDstPropertyCount()

    def _get_connection(self, index, row):
        """Override method to return connected property
        """
        src_property = self.get_connected(index).GetDstProperty(row)
        return src_property

    def _fbx_connect(self, index, fbx_property):
        res = self.get_connected(index).ConnectDstProperty(fbx_property)
        return res

    def _fbx_disconnect(self, index, fbx_property):
        res = self.get_connected(index).DisconnectDstProperty(fbx_property)
        return res

    def _fbx_disconnect_all(self, index):
        """Override method to disconnect all source objects

        TODO

        """

        res = None

        return res


class BfConnectionModelManager(object):
    def __init__(self):
        super(BfConnectionModelManager, self).__init__()

        self._scene_model = None
        self._property_model = None

        self._src_op_model = BFbxSrcObjectModel()
        self._src_oo_model = BFbxSrcObjectModel()
        self._src_pp_model = BFbxSrcPropertyModel()
        self._src_po_model = BFbxSrcPropertyModel()

        self._dst_op_model = BFbxDstObjectModel()
        self._dst_oo_model = BFbxDstObjectModel()
        self._dst_pp_model = BFbxDstPropertyModel()
        self._dst_po_model = BFbxDstPropertyModel()

        for model, parity_model in [
            (self._src_op_model, self._dst_po_model),
            (self._dst_op_model, self._src_po_model),
            (self._src_oo_model, self._dst_oo_model),
            (self._dst_oo_model, self._src_oo_model),
            (self._src_pp_model, self._dst_pp_model),
            (self._dst_pp_model, self._src_pp_model),
            (self._src_po_model, self._dst_op_model),
            (self._dst_po_model, self._src_op_model),
        ]:
            model.add_parity_model(parity_model)

        # create dummy filter models
        self._src_oo_filter = bfSceneModels.BFbxSceneDummyFilterModel()
        self._src_po_filter = bfSceneModels.BFbxSceneDummyFilterModel()
        self._dst_oo_filter = bfSceneModels.BFbxSceneDummyFilterModel()
        self._dst_po_filter = bfSceneModels.BFbxSceneDummyFilterModel()

        for model, filter_model in zip(
            self.connected_object_models(),
            self.connected_object_filter_models()
        ):
            filter_model.setSourceModel(model)

    def models(self):
        """Return all connection models.
        """
        return [
            self._src_op_model,
            self._src_oo_model,
            self._src_pp_model,
            self._src_po_model,
            self._dst_op_model,
            self._dst_oo_model,
            self._dst_pp_model,
            self._dst_po_model,
        ]

    def scene_model(self):
        return self._scene_model

    def property_model(self):
        return self._property_model

    def set_models(self, scene_model, property_model):
        """TODO check property model is asociated with scene model
        """
        self._scene_model = scene_model
        self._property_model = property_model

        for model in self.connected_object_models():
            model.setSourceModel(self._scene_model)

        for model in self.connected_property_models():
            model.setSourceModel(self._property_model)

        for model in self.object_connection_models():
            model.set_connection_model(scene_model)

        for model in self.property_connection_models():
            model.set_connection_model(property_model)

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

    def src_oo_filter(self):
        """Return source object-object connection filter model.
        """
        return self._src_oo_filter

    def src_po_filter(self):
        """Return source property-object connection filter model.
        """
        return self._src_po_filter

    def dst_oo_filter(self):
        """Return destination object-object connection filter model.
        """
        return self._dst_oo_filter

    def dst_po_filter(self):
        """Return destination property-object connection filter model.
        """
        return self._dst_po_filter

    def connected_property_models(self):
        return [
            self.src_op_model(),
            self.src_pp_model(),
            self.dst_op_model(),
            self.dst_pp_model(),
        ]

    def connected_object_models(self):
        return [
            self.src_oo_model(),
            self.src_po_model(),
            self.dst_oo_model(),
            self.dst_po_model(),
        ]

    def connected_object_filter_models(self):
        return [
            self.src_oo_filter(),
            self.src_po_filter(),
            self.dst_oo_filter(),
            self.dst_po_filter(),
        ]

    def property_connection_models(self):
        return [
            self.src_po_model(),
            self.src_pp_model(),
            self.dst_po_model(),
            self.dst_pp_model(),
        ]

    def object_connection_models(self):
        return [
            self.src_oo_model(),
            self.src_op_model(),
            self.dst_oo_model(),
            self.dst_op_model(),
        ]


class DebugView(bpQtWidgets.BpModelDebuggerTreeView):
    def __init__(self, parent=None):
        super(DebugView, self).__init__(parent=parent)

    def _child_debug(self, parent_index, row, indent=1):

        prefix = "{}[ CHILD {} ] ".format(" " * indent, row)

        child = super(DebugView, self)._child_debug(parent_index, row)

        self.debug_print("", prefix=prefix)


class Test1(Qt.QtWidgets.QWidget):
    def __init__(self, file_path, parent=None):
        super(Test1, self).__init__(parent=parent)

        self._file_path = file_path

        self._scene, self._fbx_manager = bfIO.load_file(
            self._file_path,
            fbx_manager=None
        )

        self._object_1 = self._scene.FindSrcObject("object1")

        self.create_models()
        self.create_widgets()
        self.create_layout()

        self.setGeometry(
            Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.1,
            Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.1,
            1200,
            800
        )

        self.show()

    def create_models(self):
        self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()

#         self.property_model = self.scene_model.property_model()

        self.property_model = bfPropertyModels.BFbxPropertyModel(
            self.scene_model,
            parent=None
        )

        self.scene_model.add_parity_model(self.property_model)

        self.scene_model.set_scene(self._scene, self._fbx_manager)

        self.sop_model = BFbxSrcObjectModel()
        self.soo_model = BFbxSrcObjectModel()
        self.spp_model = BFbxSrcPropertyModel()
        self.spo_model = BFbxSrcPropertyModel()

        self.dop_model = BFbxDstObjectModel()
        self.doo_model = BFbxDstObjectModel()
        self.dpp_model = BFbxDstPropertyModel()
        self.dpo_model = BFbxDstPropertyModel()

        for model in [
            self.spo_model,
            self.soo_model,
            self.dpo_model,
            self.doo_model,
        ]:
            model.setSourceModel(self.scene_model)

        for model in [
            self.spp_model,
            self.sop_model,
            self.dpp_model,
            self.dop_model,
        ]:
            model.setSourceModel(self.property_model)

    def create_widgets(self):

        self.property_view = bpQtWidgets.BpModelDebuggerTreeView()
        self.property_view.setModel(self.property_model)
        self.property_view.expandAll()

        self.property_view.setColumnWidth(0, 200)
        self.property_view.setIndentation(15)
        self.property_view.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        # connection view
        if False:
            self.sop_view = Qt.QtWidgets.QTreeView()
            self.soo_view = Qt.QtWidgets.QTreeView()
            self.spp_view = Qt.QtWidgets.QTreeView()
            self.spo_view = Qt.QtWidgets.QTreeView()
        else:
            self.sop_view = bpQtWidgets.BpModelDebuggerTreeView()
            self.soo_view = bpQtWidgets.BpModelDebuggerTreeView()
            self.spp_view = bpQtWidgets.BpModelDebuggerTreeView()
            self.spo_view = bpQtWidgets.BpModelDebuggerTreeView()

            self.dop_view = bpQtWidgets.BpModelDebuggerTreeView()
            self.doo_view = bpQtWidgets.BpModelDebuggerTreeView()
            self.dpp_view = bpQtWidgets.BpModelDebuggerTreeView()
            self.dpo_view = bpQtWidgets.BpModelDebuggerTreeView()

        for model, view in [
            (self.sop_model, self.sop_view),
            (self.soo_model, self.soo_view),
            (self.spp_model, self.spp_view),
            (self.spo_model, self.spo_view),

            (self.dop_model, self.dop_view),
            (self.doo_model, self.doo_view),
            (self.dpp_model, self.dpp_view),
            (self.dpo_model, self.dpo_view),
        ]:
            view.setModel(model)
            view.expandAll()

    def create_layout(self):
        self._lyt = Qt.QtWidgets.QHBoxLayout()
        self.setLayout(self._lyt)

        self._lyt.addWidget(self.property_view)

        self._con_lyt = Qt.QtWidgets.QVBoxLayout()
        self._src_con_lyt = Qt.QtWidgets.QHBoxLayout()
        self._dst_con_lyt = Qt.QtWidgets.QHBoxLayout()

        self._lyt.addLayout(self._con_lyt)
        self._con_lyt.addLayout(self._src_con_lyt)
        self._con_lyt.addLayout(self._dst_con_lyt)

#         self._lyt.addWidget(self.object_properties_view)
        self._src_con_lyt.addWidget(self.sop_view)
        self._src_con_lyt.addWidget(self.soo_view)
        self._src_con_lyt.addWidget(self.spp_view)
        self._src_con_lyt.addWidget(self.spo_view)

        self._dst_con_lyt.addWidget(self.dop_view)
        self._dst_con_lyt.addWidget(self.doo_view)
        self._dst_con_lyt.addWidget(self.dpp_view)
        self._dst_con_lyt.addWidget(self.dpo_view)


if __name__ == "__main__":
    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"
    TEST_PATH = os.path.join(DUMP_DIR, TEST_FILE)

    app = Qt.QtWidgets.QApplication(sys.argv)

    if True:
        test = Test1(TEST_PATH)

    sys.exit(app.exec_())
