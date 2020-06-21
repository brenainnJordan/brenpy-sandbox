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

from brenpy.qt import bpQtCore

from brenfbx.core import bfIO

from brenfbx.qt import bfSceneModels, bfQtCore


class BfConnectedProxyModelBase(bpQtCore.BpItemToListProxyModel):
    def __init__(self, parent=None):
        super(BfConnectedProxyModelBase, self).__init__(
            parent=parent
        )

    def setSourceModel(self, source_model):
        super(
            BfConnectedProxyModelBase, self
        ).setSourceModel(source_model)

    def scene_model(self):
        return self.get_root_model()

    def scene_cache(self):
        return self.scene_model().scene_cache()

    def property_cache(self):
        return self.scene_model().property_cache()

    def property_model(self):
        return self.scene_model().property_model()

    def get_connected(self, id_value):
        """Overidable method to get connected object or property
        """
        pass
#
#     def get_id_value(self, value):
#
#         if isinstance(value, Qt.QtCore.QModelIndex):
#             id_object = value.internalPointer()
#             return id_object.value()
#
#         elif isinstance(value, (int, long)):
#             return value
#
#         else:
#             # TODO
#             raise bfQtCore.BfQtError(
#                 "Failed to retreive id value: {}".format(value)
#             )
#
#     def _get_id_object(self, id_value):
#         raise bfQtCore.BfQtError(
#             "Cannot retrieve id_object from base class"
#         )
#
#     def _get_id_con_object(self, id_value):
#         raise bfQtCore.BfQtError(
#             "Cannot retrieve id_con_object from base class"
#         )
#
#     def get_id_object(self, value):
#
#         id_value = self.get_id_value(value)
#         id_object = self._get_id_object(id_value)
#
#         return id_object

    def get_id_con_object(self, value):
        #         id_value = self.get_id_value(value)
        #         id_con_object = self._get_id_con_object(id_value)
        #         return id_con_object
        raise bfQtCore.BfQtError(
            "Cannot retrieve id_con_object from base class"
        )

    def find_row(self, id_value):
        """Find row containing id_value"""

        for i in range(self.rowCount(Qt.QtCore.QModelIndex())):

            proxy_index = self.index(i, 0, Qt.QtCore.QModelIndex())

            if self.scene_model().is_dummy(proxy_index):
                continue

            if self.get_id_value(proxy_index) == id_value:
                return i

        raise bpQtCore.BpQtError(
            "Failed to find row: {}".format(id_value)
        )


class BfConnectedObjectProxyModel(BfConnectedProxyModelBase):
    def __init__(self, parent=None):
        super(BfConnectedObjectProxyModel, self).__init__(
            parent=parent
        )

#     def _get_id_object(self, object_id):
#         id_object = self.scene_model().get_id_object(object_id)
#         return id_object

    def get_id_con_object(self, object_id):
        # TODO
        return
        id_con_object = self.scene_model().get_id_con_object(object_id)
        return id_con_object

    def get_connected(self, object_id):
        """Overide method to get connected object
        """
        fbx_object = self.scene_model().get_object(object_id)
        return fbx_object

    def data(self, index, role):
        """TODO something?
        """
        super(BfConnectedObjectProxyModel, self).data(index, role)


class BfConnectedPropertyProxyModel(BfConnectedProxyModelBase):
    def __init__(self, parent=None):
        super(BfConnectedPropertyProxyModel, self).__init__(
            parent=parent
        )

#     def _get_id_object(self, property_id):
#         id_object = self.property_model().get_id_object(property_id)
#         return id_object

    def get_id_con_object(self, value):

        id_con_object = self.property_model().get_id_con_object(
            value
        )

        return id_con_object

    def data(self, index, role):
        """TODO return str path
        """
        return super(BfConnectedPropertyProxyModel, self).data(index, role)

    def get_connected(self, value):
        """Overide method to get connected property
        """
        fbx_property = self.property_model().get_fbx_property(value)
        return fbx_property


class Test1(Qt.QtWidgets.QWidget):
    def __init__(self, file_path, parent=None):
        super(Test1, self).__init__(parent=parent)

        self._file_path = file_path

        self._scene, self._fbx_manager = bfIO.load_fbx_file(
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
            800,
            800
        )

        self.show()

    def create_models(self):
        self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()
        self.scene_model.set_scene(self._scene, self._fbx_manager)

        self.property_model = self.scene_model.property_model()

        self.flat_model = BfConnectedPropertyProxyModel()
        self.flat_model.setSourceModel(self.property_model)

#         self._object_1.GetUniqueID()

#         self.scene_properties_model = bfProxyModels.BFbxScenePropertiesProxyModel()
#         self.scene_properties_model.setSourceModel(self.scene_model)

    def create_widgets(self):

        self.property_view = Qt.QtWidgets.QTreeView()
        self.property_view.setModel(self.property_model)
        self.property_view.expandAll()

        self.property_view.setColumnWidth(0, 200)
        self.property_view.setIndentation(15)
        self.property_view.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

#         # scene properties
#         self.object_properties_view = Qt.QtWidgets.QTreeView()
#         self.object_properties_view.setModel(self.property_model)
#
#         root_index = self.property_model.get_root_index(
#             self._object_1.GetUniqueID()
#         )

#         self.object_properties_view.setRootIndex(root_index)
#
#         self.object_properties_view.expandAll()

        # flat properties
        self.flat_list_view = Qt.QtWidgets.QTableView()
        self.flat_list_view.setModel(self.flat_model)

    def create_layout(self):
        self._lyt = Qt.QtWidgets.QHBoxLayout()
        self.setLayout(self._lyt)

        self._lyt.addWidget(self.property_view)
#         self._lyt.addWidget(self.object_properties_view)
        self._lyt.addWidget(self.flat_list_view)


if __name__ == "__main__":
    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"
    TEST_PATH = os.path.join(DUMP_DIR, TEST_FILE)

    app = Qt.QtWidgets.QApplication(sys.argv)

    if True:
        test = Test1(TEST_PATH)

    sys.exit(app.exec_())
