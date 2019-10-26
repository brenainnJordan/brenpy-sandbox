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
    bfFilterSettings, bfPropertyModels, bfPropertyWidgets, bfConnectionModels
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

    def __init__(self, scene_model, parent=None):
        super(BFbxPropertySelectionDialog, self).__init__(parent=parent)

        self.setWindowFlags(
            Qt.QtCore.Qt.Window | Qt.QtCore.Qt.FramelessWindowHint
        )

        self._value = None

        self.scene_model = scene_model
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

        self.line_edit.set_model(self.scene_model.property_model())

        self.line_edit.complete_signal.connect(self.completer_activated)

        if parent:
            pos = parent.mapToGlobal(parent.rect().topLeft())

            self.setGeometry(
                pos.x(),
                pos.y(),
                200,
                40
            )

    def property_model(self):
        return self.scene_model.property_model()

    def text(self):
        return self.line_edit.text()

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.QtCore.Qt.Key_Return:
            self.accept()

        super(BFbxPropertySelectionDialog, self).keyPressEvent(key_event)

    def completer_activated(self):

        property_index = self.line_edit.current_index()

        fbx_property = self.property_model().data(
            property_index,
            self.property_model().kFbxPropertyRole
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


class BfConnectionWidgetBase(Qt.QtWidgets.QWidget):
    """
    """

    SELECTION_DIALOG = BFbxObjectSelectionDialog

    def __init__(self, connection_model, parent=None):
        super(BfConnectionWidgetBase, self).__init__(parent=parent)

        self._connection_model = connection_model

        # create widgets
        self.create_widgets()
        self.create_menus()
        self.create_view()

        self.connect_menus()
#         self.connect_widgets()

        self.create_layout()

    def connection_model(self):
        return self._connection_model

    def create_widgets(self):
        pass
#         self.name_filter_edit = Qt.QtWidgets.QLineEdit()

    def connect_widgets(self):
        pass
#         self.view.setModel(self._connection_model)

    def create_menus(self):
        self.edit_menu = BfConnectionMenu()

    def create_view(self):
        self.view = Qt.QtWidgets.QTreeView()
        self.view.setModel(self._connection_model)
#         self.view.setColumnWidth(0, 300)

        self.view.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.view.setContextMenuPolicy(Qt.QtCore.Qt.CustomContextMenu)

    def model(self):
        return self.view.model()

    def connect_menus(self):

        # connect menus to widgets
        self.view.customContextMenuRequested.connect(
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

        self.edit_menu.exec_(self.mapToGlobal(position))

    def create_layout(self):
        self.main_lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self.main_lyt)

#         self.filter_lyt = Qt.QtWidgets.QHBoxLayout()
#         self.filter_lyt.addWidget(self.filter_btn)
#         self.filter_lyt.addWidget(self.name_filter_edit)

#         self.main_lyt.addLayout(self.filter_lyt)
        self.main_lyt.addWidget(self.view)

    def get_selected_root_indices(self):
        if self.view.selectionModel() is None:
            print "nothing selected"
            return

        selected = self.view.selectionModel().selection()
        return selected.indexes()

#         root_indices = []
#
#         for proxy_index in selected.indexes():
#             index = self.model().map_to_root(proxy_index)
#             root_indices.append(index)
#
#         return root_indices

    def _create_new_connection(self):
        create_dialog = self.SELECTION_DIALOG(
            self._connection_model.scene_model(),
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
            self._connection_model.fbx_connect(fbx_object)
            print fbx_object.GetName()

    def _disconnect_selected(self):
        """
        """

        selected_indices = self.get_selected_root_indices()

        self.view.selectionModel().clearSelection()

        self._connection_model.removeIndices(selected_indices)

    def _disconnect_all(self):
        """
        """

        self.view.selectionModel().clearSelection()

        self._connection_model.fbx_disconnect_all()


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
            Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.3,
            Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.3,
            400,
            400
        )

        self.show()

    def create_models(self):
        self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()
        self.scene_model.set_scene(self._scene, self._fbx_manager)

        self._connection_model_manager = bfConnectionModels.BfConnectionModelManager()
        self._connection_model_manager.set_scene_model(self.scene_model)

    def create_widgets(self):

        # connected property widgets
        self.sop_widget = BfConnectionWidgetBase(
            self._connection_model_manager.src_op_model()
        )
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

    def create_layout(self):
        self._lyt = Qt.QtWidgets.QHBoxLayout()
        self.setLayout(self._lyt)

        self._con_obj_lab_lyt = Qt.QtWidgets.QVBoxLayout()
        self._con_prop_lab_lyt = Qt.QtWidgets.QVBoxLayout()

        self._con_obj_lyt = Qt.QtWidgets.QHBoxLayout()
        self._con_prop_lyt = Qt.QtWidgets.QHBoxLayout()

        self._lyt.addLayout(self._con_obj_lab_lyt)
        self._lyt.addLayout(self._con_prop_lab_lyt)

        self._con_obj_lab_lyt.addLayout(self._con_obj_lyt)
        self._con_prop_lab_lyt.addLayout(self._con_prop_lyt)

        self._con_prop_lab_lyt.addWidget(self.sop_widget)
#         self._con_prop_lab_lyt.addWidget(self.spp_widget)


if __name__ == "__main__":

    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"
    TEST_PATH = os.path.join(DUMP_DIR, TEST_FILE)

    app = Qt.QtWidgets.QApplication(sys.argv)

    if True:
        test = Test1(TEST_PATH)

    sys.exit(app.exec_())
