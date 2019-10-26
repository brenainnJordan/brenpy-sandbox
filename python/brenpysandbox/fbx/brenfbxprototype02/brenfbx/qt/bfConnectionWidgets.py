"""Stuff

Start with object connection widget and go from there...

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
    bfFilterSettings, bfPropertyModels, bfPropertyWidgets, bfConnectionProxyModels,\
    bfQtCore, bfModelManagers
from brenfbx.qt import bfPropertyQtCache


class BpPropertyCompleter(bpQtWidgets.BpFilterCompleter):
    """Custom QCompleter configured to work with QSortFilterProxyModel

    TODO

    """

    PATH_ROLE = bfPropertyModels.BFbxPropertyModel.kPathNameRole

    def __init__(self, *args, **kwargs):
        super(BpPropertyCompleter, self).__init__(*args, **kwargs)

#     def splitPath(self, path):
#         return path.split(".")
#
#     def pathFromIndex(self, completer_index):
#         """Get source index and return model data from self.PATH_ROLE
#         """
#         filter_index = self.completionModel().mapToSource(completer_index)
#
#         filter_model = filter_index.model()
#
#         src_index = filter_model.mapToSource(filter_index)
#         src_model = src_index.model()
#
#         print "DEBUG", src_index, src_model
#
#         path = src_model.data(src_index, src_model.kPathNameRole)
#
#         print "DEBUG", path
#
#         path_str = ".".join(path)
#         print path_str
#
#         return path_str


class BFbxPropertySelectionDialog(Qt.QtWidgets.QDialog):
    """Frameless dialog to prompt user to select from available types of FbxObject.

    ** WIP **

    """

    def __init__(self, property_model, parent=None):
        super(BFbxPropertySelectionDialog, self).__init__(parent=parent)

        self.setWindowFlags(
            Qt.QtCore.Qt.Window | Qt.QtCore.Qt.FramelessWindowHint
        )

        self._value = None

        self.property_model = property_model
#
#         self.item_to_list_model = bpQtCore.BpItemToListProxyModel()
#         self.item_to_list_model.setSourceModel(self.scene_model)
#
#         self.dummy_filter_model = bfSceneModels.BFbxSceneDummyFilterModel()
#         self.dummy_filter_model.setSourceModel(self.item_to_list_model)

        # create property completer and assign to completer line edit
        self._completer = BpPropertyCompleter()

        self.line_edit = bpQtWidgets.BpCompleterLineEdit()
        self.line_edit.setCompleter(self._completer)

        # create layout
        self.lyt = Qt.QtWidgets.QVBoxLayout()
#         self.lyt.setContentsMargins(2, 2, 2, 2)

        self.setLayout(self.lyt)
        self.lyt.addWidget(self.line_edit)

        self.line_edit.set_model(self.property_model)

        self.line_edit.complete_signal.connect(self.completer_activated)

        if parent:
            pos = parent.mapToGlobal(parent.rect().topLeft())

            self.setGeometry(
                pos.x(),
                pos.y(),
                200,
                40
            )

#     def property_model(self):
#         return self.scene_model.property_model()

    def text(self):
        return self.line_edit.text()

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.QtCore.Qt.Key_Return:
            self.accept()

        super(BFbxPropertySelectionDialog, self).keyPressEvent(key_event)

    def completer_activated(self):

        property_index = self.line_edit.current_index()

        fbx_property = self.property_model.data(
            property_index,
            self.property_model.kFbxPropertyRole
        )

        self._value = fbx_property

        self.accept()

    def value(self):
        return self._value


class BFbxObjectSelectionDialog(Qt.QtWidgets.QDialog):
    """Frameless dialog to prompt user to select from available types of FbxObject.
    """

    def __init__(self, scene_model, parent=None):
        super(BFbxObjectSelectionDialog, self).__init__(parent=parent)

        self.setWindowFlags(
            Qt.QtCore.Qt.Window | Qt.QtCore.Qt.FramelessWindowHint
        )

        self._value = None

        self.scene_model = scene_model

        self.item_to_list_model = bpQtCore.BpItemToListProxyModel()
        self.item_to_list_model.setSourceModel(self.scene_model)

        self.dummy_filter_model = bfSceneModels.BFbxSceneDummyFilterModel()
        self.dummy_filter_model.setSourceModel(self.item_to_list_model)

        self.line_edit = bpQtWidgets.BpCompleterLineEdit()

        self.lyt = Qt.QtWidgets.QVBoxLayout()
#         self.lyt.setContentsMargins(2, 2, 2, 2)

        self.setLayout(self.lyt)
        self.lyt.addWidget(self.line_edit)

        self.line_edit.set_model(self.dummy_filter_model)

        self.line_edit.complete_signal.connect(self.completer_activated)

        if parent:
            pos = parent.mapToGlobal(parent.rect().topLeft())

            self.setGeometry(
                pos.x(),
                pos.y(),
                200,
                40
            )

    def text(self):
        return self.line_edit.text()

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.QtCore.Qt.Key_Return:
            self.accept()

        super(BFbxObjectSelectionDialog, self).keyPressEvent(key_event)

    def completer_activated(self):

        proxy_index = self.line_edit.current_index()

        root_index = self.dummy_filter_model.map_to_root(proxy_index)

        fbx_object = self.scene_model.data(
            root_index,
            self.scene_model.kFbxObjectRole
        )

        self._value = fbx_object

        self.accept()

    def value(self):
        return self._value


class BfConnectionMenu(Qt.QtWidgets.QMenu):
    """Edit menu
    """

    def __init__(self, parent=None):
        super(BfConnectionMenu, self).__init__(parent)

        self.setTitle("Edit")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        self.connect_action = Qt.QtWidgets.QAction(
            _icon, 'New connection', self
        )

        self.connect_action.setStatusTip(
            'Create new source object connection'
        )

        self.disconnect_action = Qt.QtWidgets.QAction(
            _icon, 'Disconnect selected', self
        )

        self.disconnect_action.setStatusTip(
            'Disconnect selected source object connections'
        )

        self.disconnect_all_action = Qt.QtWidgets.QAction(
            _icon, 'Disconnect all', self
        )

        self.disconnect_all_action.setStatusTip(
            'Disconnect all source object connections'
        )

    def _add_actions(self):

        self.addAction(self.connect_action)
        self.addAction(self.disconnect_action)
        self.addSeparator()
        self.addAction(self.disconnect_all_action)


class ViewState(object):
    """
    WIP
    * eventually move to brenpy *
    """

    def __init__(self, view):
        self._view = view
        self._root_index_path = bpQtCore.IndexPath()

    def view(self):
        return self._view

    def store(self):
        print "STORE DEBUG", self._view.rootIndex()

        self._root_index_path.set(
            self._view.rootIndex()
        )

    def restore(self):
        root_index = self._root_index_path.get(self._view.model())

        print "RESTORE DEBUG", root_index

        self._view.setRootIndex(root_index)


class BfConnectionView(Qt.QtWidgets.QTreeView):
    """
    """

    def __init__(self, parent=None):
        super(BfConnectionView, self).__init__(parent=parent)

        self._selection_dialog_cls = None

        self._view_state = ViewState(self)

        self.configure()
        self.create_menus()
        self.connect_menus()

    def setModel(self, model):
        """TODO check model
        """
        if model is self.model():
            return

        if self.model() is not None:
            self.model().modelReset.disconnect(self.restore_view_state)

        res = super(BfConnectionView, self).setModel(model)

        if model is not None:
            model.modelReset.connect(self.restore_view_state)

        return res

        # ** redundant **

        if isinstance(
            model, bfConnectionProxyModels.BFbxPropertyConnectionModelBase
        ):
            self._selection_dialog_cls = BFbxPropertySelectionDialog

        elif isinstance(
            model, bfConnectionProxyModels.BFbxObjectConnectionModelBase
        ):
            self._selection_dialog_cls = BFbxObjectSelectionDialog

        else:
            raise bfQtCore.BfQtError(
                "Model must be either object or property connection model: {}".format(
                    model
                )
            )

        res = super(BfConnectionView, self).setModel(model)

        self.expandAll()

        return res

    def model(self):
        """TODO check model?"""
        model = super(BfConnectionView, self).model()
        return model

    def get_connected_model(self):
        if isinstance(
            self.model(), (
                bfSceneModels.BFbxSceneDummyFilterModel,
            )
        ):
            return self.model().sourceModel()

        elif isinstance(
            self.model(), (
                bfConnectionProxyModels.BfConnectedProxyModelBase
            )
        ):
            return self.model()

        else:
            raise bfQtCore.BfQtError(
                "Cannot retreive connection model from unkown model type: {}".format(
                    self.model()
                )
            )

    def get_connection_model(self):

        return self.get_connected_model().connection_model()

    def create_menus(self):
        self.edit_menu = BfConnectionMenu()

    def configure(self):

        self.setSelectionMode(
            self.ExtendedSelection
        )

        self.setContextMenuPolicy(Qt.QtCore.Qt.CustomContextMenu)

    def connect_menus(self):

        # connect menus to widgets
        self.customContextMenuRequested.connect(
            self.context_menu_handler
        )

        # connect menu actions
        for action, method in [
            (self.edit_menu.connect_action, self._create_new_connection),
            (self.edit_menu.disconnect_action, self._disconnect_selected),
            (self.edit_menu.disconnect_all_action, self._disconnect_all),
        ]:
            action.triggered.connect(method)

    def context_menu_handler(self, position):
        '''
        Get information about what items are selected.
        Then show the appropriate context menu.
        '''
        if self.model() is None:
            # TODO?
            print "No model set, cannot launch menu"
            return

        self.edit_menu.exec_(self.mapToGlobal(position))

    def get_selected_connected_indices(self):
        """Return a list of indices that represent the connected
        object(s) or property(s) associated with the current selection.
        """
        connected_indices = []

        selected = self.selectionModel().selection()

        for index in selected.indexes():
            parent = index.parent()

            if not parent.isValid():
                connected = index
            else:
                connected = parent

            if connected not in connected_indices:
                connected_indices.append(connected)

        return connected_indices

    def get_connected_index(self, index):
        if isinstance(
            self.model(), (
                bfSceneModels.BFbxSceneDummyFilterModel,
            )
        ):
            source_index = self.model().mapToSource(index)

            if not source_index.isValid():
                raise bfQtCore.BfQtError(
                    "Failed to retrieve connected index: {}".format(
                        index
                    )
                )

            print "connected index :", source_index

            return source_index

        elif isinstance(
            self.model(), bfConnectionProxyModels.BfConnectedProxyModelBase
        ):
            return index

        else:
            raise bfQtCore.BfQtError(
                "Cannot retrieve connected index from unknown model type: {}".format(
                    self.model()
                )
            )

    def get_selected_connection_indices(self):
        """Return a list of selected indices that represent connections.
        """
        connection_indices = []

        selected = self.selectionModel().selection()

        for index in selected.indexes():
            index = self.get_connected_index(index)

            parent = index.parent()

            if not parent.isValid():
                continue

            if index not in connection_indices:
                connection_indices.append(index)

        return connection_indices

    def get_current_connected_index(self):
        current_index = self.selectionModel().currentIndex()

        # if nothing is selected try using root index instead
        if not current_index.isValid():
            if self.rootIndex().isValid():

                current_index = self.rootIndex()

            else:
                raise bfQtCore.BfQtError(
                    "Failed to get current index: {}".format(
                        self.model()
                    )
                )

        index = self.get_connected_index(current_index)

        if index.parent().isValid():
            connected_index = index.parent()
        else:
            connected_index = index

        index = self.model().map_to_root(index)

        return connected_index

    def get_selected_root_indices(self):
        if self.selectionModel() is None:
            print "nothing selected"
            return

        selected = self.selectionModel().selection()
        return selected.indexes()

    def store_view_state(self):
        """TODO"""
        print "storing view..."
        self._view_state.store()

    def restore_view_state(self):
        """TODO"""
        print "restoring view..."
        self._view_state.restore()
        self.expandAll()

    def create_selection_dialog(self, parent):
        raise bfQtCore.BfQtError(
            "Cannot create selection dialog from connection view base class"
        )

#         if self._selection_dialog_cls is None:
#             raise bfQtCore.BfQtError(
#                 "Selection dialog class unspecified"
#             )

#         return self._selection_dialog_cls(
#             model, parent=parent
#         )

    def _create_new_connection(self):
        print "ABOUT TO STORE"
        self.store_view_state()

        current_connected_index = self.get_current_connected_index()

        if current_connected_index is None:
            print "Nothing selected to connect to"
            return

        create_dialog = self.create_selection_dialog(
            #             self.model().scene_model(),
            parent=self.edit_menu,
        )

        if False:
            # this method is thread safe
            # but continues code before user has
            # entered data
            create_dialog.setModal(True)
            create_dialog.show()
        else:
            # using this method blocks code from continuing
            # until user has finished entering data
            create_dialog.exec_()

        if create_dialog.value() is None:
            print "Object not recognised: {}".format(
                create_dialog.text()
            )

        else:
            fbx_object = create_dialog.value()

            self.get_connected_model().fbx_connect(
                current_connected_index, fbx_object
            )

            print "Connection successful: {}".format(
                fbx_object.GetName()
            )

        print "ABOUT TO RESTORE"
        self.restore_view_state()

    def _disconnect_selected(self):
        """
        """
        self.store_view_state()

        selected_indices = self.get_selected_connection_indices()

        self.selectionModel().clearSelection()

        self.get_connected_model().removeIndices(selected_indices)

        self.restore_view_state()

    def _disconnect_all(self):
        """
        TODO confirmation dialog (or undo?)
        """
        self.store_view_state()

        selected_connected = self.get_selected_connected_indices()

        self.selectionModel().clearSelection()

        for index in selected_connected:
            self.get_connected_model().fbx_disconnect_all(index)

        self.restore_view_state()

        return True

    def setRootIndex(self, source_index):
        super(BfConnectionView, self).setRootIndex(source_index)
        print "SETTING ROOT"
        self.store_view_state()


class BfPropertyConnectionView(BfConnectionView):
    """
    """

    def __init__(self, parent=None):
        super(BfPropertyConnectionView, self).__init__(parent=parent)

    def setModel(self, model):
        """TODO check model
        """

        if not isinstance(
            model, (
                bfConnectionProxyModels.BFbxPropertyConnectionModelBase,
                bfSceneModels.BFbxSceneDummyFilterModel,
                NoneType
            )
        ):
            raise bfQtCore.BfQtError(
                "Model must be property connection model: {}".format(
                    model
                )
            )

        res = super(BfPropertyConnectionView, self).setModel(model)
        return res

    def create_selection_dialog(self, parent):
        print self.model()
        print self.get_connection_model()

        return BFbxPropertySelectionDialog(
            self.get_connection_model(), parent=parent
        )


class BfObjectConnectionView(BfConnectionView):
    """
    """

    def __init__(self, parent=None):
        super(BfObjectConnectionView, self).__init__(parent=parent)

    def setModel(self, model):
        """TODO check model
        """

        if not isinstance(
            model, (
                bfConnectionProxyModels.BFbxObjectConnectionModelBase,
                bfSceneModels.BFbxSceneDummyFilterModel,
                NoneType
            )
        ):
            raise bfQtCore.BfQtError(
                "Model must be object connection model: {}".format(
                    model
                )
            )

        res = super(BfObjectConnectionView, self).setModel(model)
        return res

    def create_selection_dialog(self, parent):

        return BFbxObjectSelectionDialog(
            self.get_connection_model(), parent=parent
        )


class BfConnectionGroupWidget(Qt.QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(BfConnectionGroupWidget, self).__init__(parent=parent)

        self._manager = None
        self._views_connected = False

        self._src_object_view = None
        self._src_property_view = None
        self._dst_object_view = None
        self._dst_property_view = None

        self.create_widgets()
#         self.create_tab_layout()
#         self.create_flat_tab_layout()
#         self.create_staggered_tab_layout()
        self.create_src_dst_tab_layout()

#         self.setGeometry(
#             Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.3,
#             Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.3,
#             400,
#             400
#         )

    def set_manager(self, connection_model_manager, connect_views=True):
        self.disconnect_views()

        self._manager = connection_model_manager

        if connect_views:
            self.connect_views()


#     def set_views_to_property_models(self):
#         for model, view in zip(
#             self._manager.connected_property_models(),
#             self.connection_views()
#         ):
#             view.setModel(model)
#
#         self.setWindowTitle("Scene properties")
#
#     def set_views_to_object_models(self):
#         for model, view in zip(
#             self._manager.connected_object_models(),
#             self.connection_views()
#         ):
#             view.setModel(model)
#
#         self.setWindowTitle("Scene objects")

    def disconnect_views(self):
        for view in self.connection_views():
            view.setModel(None)

        self._views_connected = False

    def connect_views(self):
        pass

    def views_connected(self):
        return self._views_connected

#     def set_object_index(self, source_index):
#
#         # make sure views are set to scene model
#         self.set_views_to_object_models()
#
#         if not source_index.isValid():
#
#             if False:
#                 self.disconnect_views()
#             else:
#                 for view in self.connection_views():
#                     view.set_root_index(None)
#                     view.expandAll()
#         else:
#
#             # set root index and expand view
#             for view in self.connection_views():
#                 view.set_root_index(source_index)
#                 view.expandAll()
#
#         # set widget mapping (even if None)
#         if False:
#             self._object_name_widget.setSelection(source_index)

#     def set_property_index(self, source_index):
#
#         # make sure views are set to property model
#         self.set_views_to_property_models()
#
#         if not source_index.isValid():
#
#             if False:
#                 self.disconnect_views()
#             else:
#                 for view in self.connection_views():
#                     view.set_root_index(None)
#                     view.expandAll()
#         else:
#
#             # set root index and expand view
#             for view in self.connection_views():
#                 view.set_root_index(source_index)
#                 view.expandAll()
#
#         # set widget mapping (even if None)
#         if False:
#             self._object_name_widget.setSelection(source_index)

    def create_widgets(self):
        """Stuff
        """

        self._src_object_view = BfObjectConnectionView()
        self._src_property_view = BfPropertyConnectionView()
        self._dst_object_view = BfObjectConnectionView()
        self._dst_property_view = BfPropertyConnectionView()

        self._con_label = Qt.QtWidgets.QLabel("Connections")

    def connection_views(self):
        return [
            self._src_object_view,
            self._src_property_view,
            self._dst_object_view,
            self._dst_property_view,
        ]

    def set_root_index(self, source_index):
        """Overidible method"""

        print "root poop"

        if not source_index.isValid():
            self.disconnect_views()

        elif not self.views_connected():
            print "connecting"
            self.connect_views()

        return True

#
#         self.sop_widget.set_property(
#             self._object_1.GetUniqueID(),
#             0
#         )

        # connected property widgets
#         self.spp_widget = SrcPPWidget()
#         self.spp_widget.set_scene_model(self.scene_model)
#
#         self.spp_widget.set_property(
#             self._object_1.GetUniqueID(),
#             0
#         )

    def create_debug_layout(self):
        self._lyt = Qt.QtWidgets.QHBoxLayout()
        self.setLayout(self._lyt)

        self._con_lyt = Qt.QtWidgets.QHBoxLayout()

        self._lyt.addLayout(self._con_lyt)

        for view in self.connection_views():
            self._con_lyt.addWidget(view)

    def create_layered_tab_layout(self):
        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        self._src_dst_tab_widget = Qt.QtWidgets.QTabWidget()

        self._lyt.addWidget(self._con_label)
        self._lyt.addWidget(self._src_dst_tab_widget)

        self._src_tab_widget = Qt.QtWidgets.QTabWidget()
        self._dst_tab_widget = Qt.QtWidgets.QTabWidget()

        self._src_dst_tab_widget.addTab(self._src_tab_widget, "Src")
        self._src_dst_tab_widget.addTab(self._dst_tab_widget, "Dst")

        self._src_tab_widget.addTab(self._src_object_view, "Objects")
        self._src_tab_widget.addTab(self._src_property_view, "Properties")

        self._dst_tab_widget.addTab(self._dst_object_view, "Objects")
        self._dst_tab_widget.addTab(self._dst_property_view, "Properties")

    def create_flat_tab_layout(self):
        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        self._tab_widget = Qt.QtWidgets.QTabWidget()

        self._lyt.addWidget(self._con_label)
        self._lyt.addWidget(self._tab_widget)

        self._tab_widget.addTab(self._src_object_view, "Src Objects")
        self._tab_widget.addTab(self._src_property_view, "Src Properties")
        self._tab_widget.addTab(self._dst_object_view, "Dst Objects")
        self._tab_widget.addTab(self._dst_property_view, "Dst Properties")

    def create_staggered_tab_layout(self):
        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        self._object_tab_widget = Qt.QtWidgets.QTabWidget()
        self._property_tab_widget = Qt.QtWidgets.QTabWidget()

        self._lyt.addWidget(self._con_label)
        self._lyt.addWidget(self._object_tab_widget)
        self._lyt.addWidget(self._property_tab_widget)

        self._object_tab_widget.addTab(
            self._src_object_view, "Src Objects"
        )

        self._object_tab_widget.addTab(
            self._dst_object_view, "Dst Objects"
        )

        self._property_tab_widget.addTab(
            self._src_property_view, "Src Properties"
        )

        self._property_tab_widget.addTab(
            self._dst_property_view, "Dst Properties"
        )

    def create_src_dst_tab_layout(self):

        for view in self.connection_views():
            view.setHeaderHidden(True)

        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        self._tab_widget = Qt.QtWidgets.QTabWidget()

        self._src_widget = Qt.QtWidgets.QWidget()
        self._dst_widget = Qt.QtWidgets.QWidget()

        self._src_lyt = Qt.QtWidgets.QVBoxLayout()
        self._dst_lyt = Qt.QtWidgets.QVBoxLayout()

        self._src_widget.setLayout(self._src_lyt)
        self._dst_widget.setLayout(self._dst_lyt)

        self._src_lyt.addWidget(self._src_object_view)
        self._src_lyt.addWidget(self._src_property_view)

        self._dst_lyt.addWidget(self._dst_object_view)
        self._dst_lyt.addWidget(self._dst_property_view)

        self._lyt.addWidget(self._tab_widget)

        self._tab_widget.addTab(self._src_widget, "Src Connections")
        self._tab_widget.addTab(self._dst_widget, "Dst Connections")


class BfConnectedPropertyWidget(BfConnectionGroupWidget):

    def __init__(self, parent=None):
        super(BfConnectedPropertyWidget, self).__init__(parent=parent)

        self.setWindowTitle("Connected Properties")

    def connect_views(self):
        super(BfConnectedPropertyWidget, self).connect_views()

        for model, view in zip(
            self._manager.connected_property_models(),
            self.connection_views()
        ):
            view.setModel(model)

        self._views_connected = True

    def set_root_index(self, source_index):
        super(BfConnectedPropertyWidget, self).set_root_index(source_index)

        for model, view in zip(
            self._manager.connected_property_models(),
            self.connection_views()
        ):
            proxy_index = model().mapFromSource(source_index)
            print "debug property proxy index", proxy_index
            view.setRootIndex(proxy_index)


class BfConnectedObjectWidget(BfConnectionGroupWidget):

    def __init__(self, parent=None):
        super(BfConnectedObjectWidget, self).__init__(parent=parent)

    def connect_views(self):
        super(BfConnectedObjectWidget, self).connect_views()

        for model, view in zip(
            self._manager.connected_object_filter_models(),
            self.connection_views()
        ):
            view.setModel(model)

        self._views_connected = True

    def set_root_index(self, source_index):
        super(BfConnectedObjectWidget, self).set_root_index(source_index)

        for model, filter_model, view in zip(
            self._manager.connected_object_models(),
            self._manager.connected_object_filter_models(),
            self.connection_views()
        ):
            proxy_index = model.mapFromSource(source_index)
            filter_index = filter_model.mapFromSource(proxy_index)

            view.setRootIndex(filter_index)

            if view.rootIndex() != filter_index:
                print "root index error..."
                print "  debug object proxy index", proxy_index
                print "  debug object filter index", filter_index
                print "  debug filter index model", filter_index.model()
                print "  debug view model", view.model()


class Test1(Qt.QtWidgets.QWidget):
    """Test connection view with single connection model
    """

    def __init__(self, file_path, parent=None):
        super(Test1, self).__init__(parent=parent)

        self._file_path = file_path

        self._scene, self._fbx_manager = bfIO.load_file(
            self._file_path,
            fbx_manager=None
        )

        self.create_models()
        self.create_widgets()
        self.create_layout()

        self.setGeometry(
            Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.3,
            Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.3,
            400,
            400
        )

        self.show()

    def create_models(self):
        self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()

        self.property_model = bfPropertyModels.BFbxPropertyModel(
            self.scene_model,
            parent=None
        )

        self.scene_model.add_parity_model(self.property_model)

        self.scene_model.set_scene(self._scene, self._fbx_manager)

        self._model_manager = bfConnectionProxyModels.BfConnectionModelManager()
        self._model_manager.set_models(self.scene_model, self.property_model)
#         self._model_manager.set_scene_model(self.scene_model)

    def create_widgets(self):

        # connected property widgets
        self.sop_widget = BfConnectionView()

        self.sop_widget.setModel(
            self._model_manager.src_op_model()
        )

    def create_layout(self):
        self._lyt = Qt.QtWidgets.QHBoxLayout()
        self.setLayout(self._lyt)

        self._lyt.addWidget(self.sop_widget)


class Test2(Qt.QtWidgets.QWidget):
    """Test connection group widget
    """

    def __init__(self, file_path, parent=None):
        super(Test2, self).__init__(parent=parent)

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
            Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.3,
            Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.3,
            400,
            400
        )

        self.show()

    def create_models(self):
        #         self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()
        #         self.scene_model.set_scene(self._scene, self._fbx_manager)

        self._model_manager = bfModelManagers.BfSceneModelManager()
        self._model_manager.set_scene(self._scene, self._fbx_manager)

#         self._con_model_manager = bfConnectionProxyModels.BfConnectionModelManager()
        #         self._model_manager.set_scene_model(self.scene_model)

    def create_widgets(self):

        self.obj_con_widget = BfConnectedObjectWidget()
        self.prop_con_widget = BfConnectedPropertyWidget()

        self.obj_con_widget.set_manager(
            self._model_manager.connection_model_manager()
        )

        self.prop_con_widget.set_manager(
            self._model_manager.connection_model_manager()
        )

#         self.obj_con_widget.set_root_index(
#
#         )

#         self.prop_con_widget.set_views_to_property_models()
#         self.obj_con_widget.set_views_to_object_models()

    def create_layout(self):
        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        self._lyt.addWidget(self.obj_con_widget)
        self._lyt.addWidget(self.prop_con_widget)


if __name__ == "__main__":

    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"
    TEST_PATH = os.path.join(DUMP_DIR, TEST_FILE)

    app = Qt.QtWidgets.QApplication(sys.argv)

    if False:
        test = Test1(TEST_PATH)
    elif True:
        test = Test2(TEST_PATH)

    sys.exit(app.exec_())
