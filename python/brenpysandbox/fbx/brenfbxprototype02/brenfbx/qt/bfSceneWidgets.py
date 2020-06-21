"""

TODO

2 methods of creating objects

method 1:
User friendly hierarchy of menus with categories of objects,
all types are visible to choose from list.

Requires no prior user knowledge of object type names.

method 2:
Type model, user starts typing name of object type into line edit
and is given a list of matching types to select.

Requires user to have rough idea of how object types are named.

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
from brenpy.qt import bpQtWidgets

from brenfbx.core import bfIO

from brenfbx.qt import bfQtWidgets, bfSceneMenus, bfSceneModels, bfDataModels,\
    bfFilterSettings, bfPropertyWidgets
from brenfbx.qt import bfModelManagers
from brenfbx.qt import bfConnectionWidgets


class BFbxTypeSelectionDialog(Qt.QtWidgets.QDialog):
    """Frameless dialog to prompt user to select from available types of FbxObject.
    """

    def __init__(self, parent=None):
        super(BFbxTypeSelectionDialog, self).__init__(parent=parent)

        self.setWindowFlags(
            Qt.QtCore.Qt.Window | Qt.QtCore.Qt.FramelessWindowHint
        )

        self._value = None

        self.model = bfDataModels.BFbxTypeModel()

        self.line_edit = bpQtWidgets.BpCompleterLineEdit()

        self.lyt = Qt.QtWidgets.QVBoxLayout()
#         self.lyt.setContentsMargins(2, 2, 2, 2)

        self.setLayout(self.lyt)
        self.lyt.addWidget(self.line_edit)

        self.line_edit.set_model(self.model, hierarchy=False)

        self.line_edit.complete_signal.connect(self.completer_activated)

        if parent:
            pos = parent.mapToGlobal(parent.rect().center())

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

        super(BFbxTypeSelectionDialog, self).keyPressEvent(key_event)

    def completer_activated(self):
        fbx_cls = self.model.data(
            self.line_edit.current_index(),
            self.model.kFbxClassRole
        )

        self._value = fbx_cls

        self.accept()

    def value(self):
        return self._value


class BFbxClassIdBoolView(Qt.QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(BFbxClassIdBoolView, self).__init__()

#         self.setColumnWidth(0, 300)
#         self.setIndentation(15)

        self._last_file_path = None

        self.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.setContextMenuPolicy(Qt.QtCore.Qt.CustomContextMenu)

        self.setHeaderHidden(True)

        self.customContextMenuRequested.connect(
            self._context_menu_handler
        )

        self.context_menu = bfSceneMenus.BFbxClassIdBoolMenu()
        self._connect_menu()

    def _connect_menu(self):
        for action, method in [
            (self.context_menu.select_all, self.select_all),
            (self.context_menu.deselect_all, self.deselect_all),
            (self.context_menu.toggle_all, self.toggle_all),

            (self.context_menu.check_all, self.check_all),
            (self.context_menu.uncheck_all, self.uncheck_all),
            (self.context_menu.toggle_all, self.toggle_all),

            (self.context_menu.check_selected, self.check_selected),
            (self.context_menu.uncheck_selected, self.uncheck_selected),
            (self.context_menu.toggle_selected, self.toggle_selected),

            (self.context_menu.export_data, self.export_data),
            (self.context_menu.import_data, self.import_data),

        ]:
            action.triggered.connect(method)

    def _context_menu_handler(self, position):
        """Show context menu.
        """
        self.context_menu.exec_(self.mapToGlobal(position))

    def select_all(self):
        self.selectAll()

    def deselect_all(self):
        self.clearSelection()

    def invert_selection(self):
        self.selectionModel().select(
            Qt.QtCore.QModelIndex(),
            self.selectionModel().Toggle
        )

    def export_data(self):

        file_path, file_type = Qt.QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Export file',
            self._last_file_path,
            "Json files (*.json)"
        )

        if file_path == "":
            print "cancelled"
            return

        if os.path.exists(file_path):
            print(['overwriting ', file_path])

        with file(file_path, "w") as f:
            str_data = self.model().serialize()
            f.write(str_data)

    def import_data(self):
        file_path, file_type = Qt.QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Import file',
            self._last_file_path,
            "Json files (*.json)"
        )

        if file_path == "":
            print "cancelled"
            return

        if os.path.exists(file_path):
            with file(file_path, "r") as f:
                str_data = f.read()
                self.model().deserialize(str_data)
                self.expandAll()

        return True

    def toggle_selected(self):
        for index in self.selectionModel().selectedIndexes():
            current_state = self.model().data(
                index, Qt.QtCore.Qt.CheckStateRole
            )

            if current_state == Qt.QtCore.Qt.Checked:
                self.model().setData(
                    index, Qt.QtCore.Qt.Unchecked, Qt.QtCore.Qt.CheckStateRole
                )
            elif current_state == Qt.QtCore.Qt.Unchecked:
                self.model().setData(
                    index, Qt.QtCore.Qt.Checked, Qt.QtCore.Qt.CheckStateRole
                )
            else:
                print "State not recognised: {} {}".format(
                    current_state, index
                )

    def check_selected(self):
        for index in self.selectionModel().selectedIndexes():
            self.model().setData(
                index, Qt.QtCore.Qt.Checked, Qt.QtCore.Qt.CheckStateRole
            )

    def uncheck_selected(self):
        for index in self.selectionModel().selectedIndexes():
            self.model().setData(
                index, Qt.QtCore.Qt.Unchecked, Qt.QtCore.Qt.CheckStateRole
            )

    def check_all(self):
        pass

    def uncheck_all(self):
        pass

    def toggle_all(self):
        pass


class BFbxTypeFilterSettingsWidget(Qt.QtWidgets.QWidget):
    def __init__(self, filter_settings, parent=None):
        super(BFbxTypeFilterSettingsWidget, self).__init__(parent=parent)

        self._settings = filter_settings

        # create models
        self._create_models()

        # create view
        self.view = BFbxClassIdBoolView()

        # create combo
        self.model_combo = Qt.QtWidgets.QComboBox()

        self.model_combo.addItems(
            self._settings.fbx_type_settings().model_type_names()
        )

        self.model_combo.activated.connect(self._switch_model)

        self.model_combo.setCurrentIndex(
            self._settings.fbx_type_settings().model_type_index()
        )

        # set view model
        self._switch_model(
            self._settings.fbx_type_settings().model_type_index()
        )

        # create layout
        self.lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self.lyt)
        self.lyt.addWidget(self.model_combo)
        self.lyt.addWidget(self.view)

    def _create_models(self):
        self._types_list_model = bfDataModels.BFbxClassIdBoolListModel()
        self._types_tree_model = bfDataModels.BFbxClassIdBoolTreeModel()

        self._types_list_model.set_data_root(
            self._settings.fbx_type_settings().data_root()
        )

        self._types_tree_model.set_data_root(
            self._settings.fbx_type_settings().data_root()
        )

    def _switch_model(self, index):
        res = self._settings.fbx_type_settings().set_model_type_index(index)

        if res:
            if index == 0:
                self.view.setModel(self._types_list_model)
            elif index == 1:
                self.view.setModel(self._types_tree_model)
                self.view.expandAll()

            return True
        else:
            print "combo out of range?!"
            return False


class BFbxFilterSettingsDialog(Qt.QtWidgets.QDialog):
    """Frameless dialog to allow user to edit filter settings.
    """

    def __init__(self, filter_settings, parent=None):
        super(BFbxFilterSettingsDialog, self).__init__(parent=parent)

#         self.setWindowFlags(
#             Qt.QtCore.Qt.Window | Qt.QtCore.Qt.FramelessWindowHint
#         )

        self.filter_settings = filter_settings

        self._create_widgets()
        self._create_tabs()
        self._create_layout()
#         self._create_models()
        self._connect_widgets()

        self.setSizeGripEnabled(True)

        if parent:
            pos = parent.mapToGlobal(parent.rect().center())

            self.setGeometry(
                pos.x(),
                pos.y(),
                300,
                500
            )

    def _create_tabs(self):
        self.tab_widget = Qt.QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.fbx_types_widget, "fbx types")
#         self.tab_widget.addTab(self.widget_2, "Tab2")
#         self.tab_widget.addTab(self.widget_3, "Tab3")

    def _create_widgets(self):
        self._accept_btn = Qt.QtWidgets.QPushButton("Accept")
        self._reject_btn = Qt.QtWidgets.QPushButton("Cancel")

        self.fbx_types_widget = BFbxTypeFilterSettingsWidget(
            self.filter_settings, parent=self
        )

#     def set_fbx_types_model(self, model):
#         self.fbx_types_model = model
#         self.fbx_types_view.setModel(self.fbx_types_model)
#         self.fbx_types_view.expandAll()

    def _connect_widgets(self):
        self._accept_btn.clicked.connect(self.accept)
        self._reject_btn.clicked.connect(self.reject)

        self._accept_btn.setDefault(True)

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QVBoxLayout()
#         self.lyt.setContentsMargins(2, 2, 2, 2)

        self.btn_lyt = Qt.QtWidgets.QHBoxLayout()
        self.btn_lyt.addWidget(self._reject_btn)
        self.btn_lyt.addWidget(self._accept_btn)

        self.setLayout(self.lyt)
        self.lyt.addWidget(self.tab_widget)
        self.lyt.addLayout(self.btn_lyt)


class BfSceneTreeView(Qt.QtWidgets.QTreeView):
    """

    TODO debug what's causing random setData calls of scene model
    when cancelling new connections!

    """

    def __init__(self, parent=None):
        super(BfSceneTreeView, self).__init__(parent=parent)

    def debug(self, msg):
        print "[ BfSceneTreeView ] {}".format(msg)

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.QtCore.Qt.Key_Return:
            self.debug("Return pressed")
        else:
            self.debug("Key pressed: {}".format(key_event.key()))

        super(BfSceneTreeView, self).keyPressEvent(key_event)


class BfSceneTreeWidget(Qt.QtWidgets.QWidget):
    """Widget to view and edit object in a FbxScene

    More than one widget can be instanced and interact with the same scene.

    This is made possible by widgets sharing the same scene Qt model.

    """

    def __init__(self, parent=None):
        super(BfSceneTreeWidget, self).__init__(parent=parent)

        # widget depends on a specific filter model to function
        self._name_filter_model = bfSceneModels.BFbxSceneHierarchyNameFilterModel()
        self._type_filter_model = bfSceneModels.BFbxSceneTypeFilterModel()

        # filter settings are managed via BfSceneFilterSettings object
        self._filter_settings = bfFilterSettings.BfSceneFilterSettings()
        self._filter_settings.debug()

        # create widgets
        self.create_widgets()
        self.create_menus()
        self.create_view()

        self.connect_menus()
        self.connect_widgets()

        self.create_layout()

    def filter_settings(self):
        return self._filter_settings

    def create_widgets(self):
        self.create_btn = Qt.QtWidgets.QPushButton("+")
        self.edit_btn = Qt.QtWidgets.QPushButton("...")

        self.filter_btn = Qt.QtWidgets.QPushButton()

        self.filter_icon = self.style().standardIcon(
            Qt.QtWidgets.QStyle.SP_FileDialogListView
        )

        self.filter_btn.setIcon(self.filter_icon)

        self.name_filter_edit = Qt.QtWidgets.QLineEdit()

    def connect_widgets(self):

        self._type_filter_model.setSourceModel(self._name_filter_model)
        self.view.setModel(self._type_filter_model)

        self._type_filter_model.set_fbx_types(
            self._filter_settings.fbx_type_settings().enabled_class_ids()
        )

        self.filter_btn.clicked.connect(
            self._filter_btn_clicked
        )

        self.name_filter_edit.textChanged.connect(
            self._filter_edit_changed
        )

        self.create_btn.clicked.connect(
            self._create_clicked
        )

    def create_menus(self):
        self.edit_menu = bfSceneMenus.BfEditMenu()

    def create_view(self):
        #         self.view = Qt.QtWidgets.QTreeView()
        self.view = BfSceneTreeView()
#         self.view.setModel(self.scene_model)
#         self.view.expandAll()

        self.view.setColumnWidth(0, 300)
        self.view.setIndentation(15)

        self.view.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self.view.setContextMenuPolicy(Qt.QtCore.Qt.CustomContextMenu)

    def set_scene_model(self, scene_model):
        """
        """
        self._name_filter_model.setSourceModel(scene_model)

        self.view.setColumnWidth(0, 200)
        self.view.expandAll()

    def model(self):
        return self.view.model()

    def get_root_model(self):
        return self._name_filter_model.get_root_model()

    def connect_menus(self):

        # connect menus to widgets
        self.view.customContextMenuRequested.connect(
            self.context_menu_handler
        )

        self.edit_btn.setMenu(self.edit_menu)

        # connect menu actions
        for action, method in [
            (self.edit_menu.delete_action, self._delete_selected),
            (self.edit_menu.parent_action, self._parent_selected),
            (self.edit_menu.unparent_action, self._unparent_selected),
        ]:
            action.triggered.connect(method)

    def context_menu_handler(self, position):
        '''
        Get information about what items are selected.
        Then show the appropriate context menu.
        '''

        self.edit_menu.exec_(self.mapToGlobal(position))

        # TODO
#
#         ids = self.tree.selectedIndexes()
#         node_items = self.get_selected_node_items()
#
#         if len(ids) == 2 and len(node_items) == 1:
#             self.single_node_and_root_context_menu(position, node_items[0])
#         elif len(ids) > len(node_items):
#             self.multi_node_and_root_context_menu(position, node_items)
#         elif len(node_items) == 1:
#             self.single_node_context_menu(position, node_items[0])
#         elif len(node_items) > 1:
#             self.multi_node_context_menu(position, node_items)
#         else:
#             self.root_context_menu(position)
#
#     def single_node_and_root_context_menu(self, position, item):
#         '''
#         Context menu for when root and one node is selected
#         '''
#         menu = QtGui.QMenu(self)
#         prnt_action = menu.addAction('Parent to Root')
#
#         action = menu.exec_(self.mapToGlobal(position))
#         if action == prnt_action:
#             self.parent_item_and_node(item, self.root_item)

    def create_layout(self):
        self.main_lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self.main_lyt)

        self.btn_lyt = Qt.QtWidgets.QHBoxLayout()
        self.btn_lyt.addWidget(self.create_btn)
        self.btn_lyt.addWidget(self.edit_btn)
        self.btn_lyt.addStretch()

        self.filter_lyt = Qt.QtWidgets.QHBoxLayout()
        self.filter_lyt.addWidget(self.filter_btn)
        self.filter_lyt.addWidget(self.name_filter_edit)

        self.main_lyt.addLayout(self.btn_lyt)
        self.main_lyt.addLayout(self.filter_lyt)
        self.main_lyt.addWidget(self.view)

    def _filter_edit_changed(self):
        # get filter value
        value = self.name_filter_edit.text()

        # reset highlighted indices and set new filter
        self._name_filter_model._highlighted_indices.clear()

        # use wildcards either side for convinience
        if value != "":
            value = "*{}*".format(value)

        self._name_filter_model.setFilterWildcard(value)

        # show all results
        # TODO change this to only expand to matching results
        self.view.expandAll()

    def _filter_btn_clicked(self):

        # make a temporary copy of filter settings
        edited_filter_settings = bfFilterSettings.BfSceneFilterSettings()

        edited_filter_settings.deserialize(
            self._filter_settings.serialize()
        )

        edited_filter_settings.debug()

        # launch dialog to edit settings
        filter_setting_dialog = BFbxFilterSettingsDialog(
            edited_filter_settings, parent=self.filter_btn
        )

        res = filter_setting_dialog.exec_()

        # if not cancelled, transfer edited settings
        if res == Qt.QtWidgets.QDialog.Rejected:
            print "cancelled"
            return

        self._filter_settings.deserialize(
            edited_filter_settings.serialize()
        )

        self._type_filter_model.set_fbx_types(
            self._filter_settings.fbx_type_settings().enabled_class_ids()
        )

        self.view.expandAll()

    def _create_clicked(self):
        create_dialog = BFbxTypeSelectionDialog(
            parent=self.create_btn
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
            print "Object type not recognised: {}".format(
                create_dialog.text()
            )

        else:
            fbx_cls = create_dialog.value()
            self.get_root_model().create_object(fbx_cls, name=None)
            self.view.expandAll()

    def get_selected_root_indices(self):
        if self.view.selectionModel() is None:
            print "nothing selected"
            return

        selected = self.view.selectionModel().selection()

        root_indices = []

        for proxy_index in selected.indexes():
            index = self.model().map_to_root(proxy_index)
            root_indices.append(index)

        return root_indices

    def _delete_selected(self):
        """Simple test for deleting objects selected in the "main" view
        Ideally this should be managed by a view widget.
        """

        selected_indices = self.get_selected_root_indices()
        self.view.selectionModel().clearSelection()

        self.get_root_model().removeIndices(selected_indices)

        self.view.expandAll()

    def _parent_selected(self):

        selected_indices = self.get_selected_root_indices()

        self.get_root_model().add_node_children(selected_indices)

        # TODO maintain current view expansion
        self.view.expandAll()

    def _unparent_selected(self):
        selected_indices = self.get_selected_root_indices()

        self.view.selectionModel().clearSelection()

        self.get_root_model().unparent_nodes(selected_indices)

        self.view.expandAll()


class BFbxPropertyWidget(Qt.QtWidgets.QWidget):
    def __init__(self, scene_model=None, parent=None):
        super(BFbxPropertyWidget, self).__init__(parent)

        self._debug_print = True

        # placeholder model
        self._filter_model = bpQtCore.BpSortFilterProxyModel()

#         self._scene_model = scene_model
        self._model_manager = None

        self._fbx_manager = None
        self._fbx_scene = None

        self._create_widgets()
        self._create_layout()
#         self._connect_widgets()

    def _create_widgets(self):

        self._object_name_widget = bfQtWidgets.BfObjectNameWidget()
        self._object_type_widget = bfQtWidgets.BfObjectTypeWidget()

        # name/type widgets
        self._name_type_frame = Qt.QtWidgets.QFrame()

        self._name_type_frame.setFrameStyle(
            #             Qt.QtWidgets.QFrame.Panel | Qt.QtWidgets.QFrame.Plain
            Qt.QtWidgets.QFrame.StyledPanel | Qt.QtWidgets.QFrame.Plain
            #             Qt.QtWidgets.QFrame.Panel | Qt.QtWidgets.QFrame.Raised
        )

#         self._name_type_frame.setFrameShape(
#             Qt.QtWidgets.QFrame.StyledPanel
#         )

        self._name_type_frame.setLineWidth(3)
        self._name_type_frame.setMidLineWidth(3)

        self._name_type_frame.setSizePolicy(
            Qt.QtWidgets.QSizePolicy.Minimum,
            Qt.QtWidgets.QSizePolicy.Fixed
        )

        self._name_type_frame.setFixedHeight(75)

        # property view
        self.property_view = Qt.QtWidgets.QTreeView()
        self.property_view.setModel(self._filter_model)

        # property edit deligate
        self.property_deligate = bfPropertyWidgets.PropertyFnStrDeligate(
            parent=self.property_view
        )

        self.property_view.setItemDelegate(
            self.property_deligate
        )

        self.property_view.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        # property frame
        self._property_frame = Qt.QtWidgets.QFrame()

        self._property_frame.setFrameStyle(
            Qt.QtWidgets.QFrame.StyledPanel | Qt.QtWidgets.QFrame.Sunken
            #             QtGui.QFrame.Panel | QtGui.QFrame.Raised
        )

        self._property_frame.setLineWidth(1)

    def _create_layout(self):

        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        # name/type layout
        self._name_type_lyt = Qt.QtWidgets.QVBoxLayout()
#         self._name_type_lyt.setContentsMargins(5, 5, 5, 5)
#         self._name_type_lyt.setSpacing(5)
        self._name_type_frame.setLayout(self._name_type_lyt)

        self._name_type_lyt.addWidget(self._object_name_widget)
        self._name_type_lyt.addWidget(self._object_type_widget)

        self._lyt.addWidget(self._name_type_frame)
        self._lyt.addWidget(self._property_frame)

        # property layout
        self._property_lyt = Qt.QtWidgets.QVBoxLayout()
        self._property_frame.setLayout(self._property_lyt)

        self._property_lyt.addWidget(self.property_view)

    def set_scene_model(self, scene_model):

        self._scene_model = scene_model

        self._object_name_widget.setModel(self._scene_model)
        self._object_type_widget.setModel(self._scene_model)

        # clear property view by passing empty index
        self.set_object_index(Qt.QtCore.QModelIndex())

    def model(self):
        return self.property_view.model()

    def scene_model(self):
        return self._model_manager.scene_model()

    def property_model(self):
        return self._model_manager.property_model()

    def set_model_manager(self, model_manager):
        self._model_manager = model_manager

        self._object_name_widget.setModel(self.scene_model())
        self._object_type_widget.setModel(self.scene_model())

        # clear property view by passing empty index
        self.set_object_index(Qt.QtCore.QModelIndex())

    def set_object_index(self, object_index):

        #         property_model = self._scene_model.get_property_model()
        #         self.property_view.setModel(property_model)

        if not object_index.isValid():

            #             self.property_view.setModel(None)
            self._filter_model.setSourceModel(None)

        else:
            # make sure view is set to property model
            #             self.property_view.setModel(
            #                 self.property_model()
            #             )
            self._filter_model.setSourceModel(self.property_model())

            # find root index
            fbx_object_id = self.scene_model().get_fbx_object_id(object_index)

            if fbx_object_id is None:
                # TODO raise?
                root_index = Qt.QtCore.QModelIndex()
            else:
                root_index = self.property_model().get_root_index(
                    fbx_object_id
                )

            filter_index = self._filter_model.mapFromSource(root_index)

            # set root index and expand view
            self.property_view.setRootIndex(filter_index)
            self.property_view.expandAll()

        # set widget mapping (even if None)
        self._object_name_widget.setSelection(object_index)
        self._object_type_widget.setSelection(object_index)


class BFbxSceneWidget(Qt.QtWidgets.QWidget):
    """Contains scene tree view and property editor
    """

    def __init__(self, parent=None):
        super(BFbxSceneWidget, self).__init__(parent)

        self._debug_print = True

        self._model_manager = None
#         self._fbx_manager = None
#         self._fbx_scene = None

        self._create_widgets()
        self._create_layout()
#         self._create_model()
        self._connect_widgets()

    def debug(self, msg):
        '''
        print in context
        # TODO proper logging
        '''

        if self._debug_print:
            print "[ BFbxSceneWidget ] {}".format(msg)

    def _create_widgets(self):
        """
        """

        self._tree_widget = BfSceneTreeWidget()

        self._property_widget = BFbxPropertyWidget()

#         self._object_connections_widget = bfConnectionWidgets.BfConnectionGroupWidget()
#         self._property_connections_widget = bfConnectionWidgets.BfConnectionGroupWidget()
        self._object_connections_widget = bfConnectionWidgets.BfConnectedObjectWidget()
        self._property_connections_widget = bfConnectionWidgets.BfConnectedPropertyWidget()

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.setLayout(self.lyt)

        self.lyt_splitter = Qt.QtWidgets.QSplitter()
        self.lyt_splitter.setOrientation(Qt.QtCore.Qt.Horizontal)
#         self.lyt_splitter.setHandleWidth(1)
#         self.lyt_splitter.setRubberBand(100)

        self._scene_splitter = Qt.QtWidgets.QSplitter()
        self._scene_splitter.setOrientation(Qt.QtCore.Qt.Vertical)

        self._scene_splitter.addWidget(self._tree_widget)
        self._scene_splitter.addWidget(self._object_connections_widget)

        self._scene_splitter.setCollapsible(1, True)
        self._scene_splitter.setStretchFactor(0, 1)
#         self._scene_splitter.setSizes([1000, 1])

        self._property_splitter = Qt.QtWidgets.QSplitter()
        self._property_splitter.setOrientation(Qt.QtCore.Qt.Vertical)

        self._property_splitter.addWidget(self._property_widget)
        self._property_splitter.addWidget(self._property_connections_widget)

        self._property_splitter.setCollapsible(1, True)
        self._property_splitter.setStretchFactor(0, 1)

        self.lyt_splitter.addWidget(self._scene_splitter)
        self.lyt_splitter.addWidget(self._property_splitter)

#         self.lyt_splitter.addWidget(self._tree_widget)
#         self.lyt_splitter.addWidget(self._property_widget)

        self.lyt_splitter.setSizes([50, 100])

        self.lyt.addWidget(self.lyt_splitter)

        # temp
        self._object_connections_widget.show()
        self._property_connections_widget.show()

#     def set_scene_model(self, scene_model):
#         self._tree_widget.set_scene_model(scene_model)
#         self._property_widget.set_scene_model(scene_model.get_root_model())

    def scene_model(self):
        return self._model_manager.scene_model()

    def scene_filter_model(self):
        return self._model_manager.scene_filter_model()

    def set_model_manager(self, model_manager):

        self._model_manager = model_manager

        self._tree_widget.set_scene_model(self.scene_filter_model())

        self._property_widget.set_model_manager(
            model_manager
        )

        self._object_connections_widget.set_manager(
            model_manager.connection_model_manager(), connect_views=False
        )
#         self._object_connections_widget.set_views_to_object_models()

        self._property_connections_widget.set_manager(
            model_manager.connection_model_manager(), connect_views=False
        )
#         self._property_connections_widget.set_views_to_property_models()

#         self._connect_widgets()

    def _connect_widgets(self):

        # connect object selection
        Qt.QtCore.QObject.connect(
            self._tree_widget.view.selectionModel(),
            SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
            self._tree_current_changed
        )

        Qt.QtCore.QObject.connect(
            self._tree_widget.view.selectionModel(),
            SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
            self._tree_selection_changed
        )

        return

        # TODO!

        # connect property selection
        Qt.QtCore.QObject.connect(
            self._property_widget.property_view.selectionModel(),
            SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
            self._property_current_changed
        )

        Qt.QtCore.QObject.connect(
            self._property_widget.property_view.selectionModel(),
            SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
            self._property_selection_changed
        )

    def _tree_selection_changed(self, new_selected, new_deselected):
        """Update widgets with multiple or empty index selections.
        Normally called before self._tree_current_changed().
        """
        selected = self._tree_widget.view.selectionModel().selection()

#         print "selection changed"

        if len(selected):
            # get last selected index
            #             index = selected.indexes()[-1]
            selected_index = self._tree_widget.view.selectionModel().currentIndex()

            index = self._tree_widget.model().map_to_root(selected_index)
# #                 old_index = self._proxy_model.mapToSource(old_index)

        else:
            # set invalid index to indicate empty selection
            index = Qt.QtCore.QModelIndex()

        self._set_property_view_index(index)
        self._set_object_connections_index(index)

    def _tree_current_changed(self, index, old_index):
        """Update corresponding widgets to current selected index.
        Normally called after self._tree_selection_changed().
        """

        src_index = self._tree_widget.model().map_to_root(index)
        src_old_index = self._tree_widget.model().map_to_root(old_index)

        self._set_property_view_index(src_index)
        self._set_object_connections_index(src_index)

#         print "current changed"

    def _property_selection_changed(self, new_selected, new_deselected):
        """stuff.
        """
        selected = self._property_widget.property_view.selectionModel().selection()

#         print "selection changed"

        if len(selected):
            # get last selected index
            #             index = selected.indexes()[-1]
            selected_index = self._property_widget.model().selectionModel().currentIndex()
            index = self._property_widget.model().map_to_root(selected_index)

#             index = self._property_widget.model().map_to_root(selected_index)
# # #                 old_index = self._proxy_model.mapToSource(old_index)

        else:
            # set invalid index to indicate empty selection
            index = Qt.QtCore.QModelIndex()

        self._set_property_connections_index(index)

    def _property_current_changed(self, index, old_index):
        """stuff
        """

        src_index = self._property_widget.model().map_to_root(index)
        src_old_index = self._property_widget.model().map_to_root(old_index)
        print "weofhwfio"
        self._set_property_connections_index(src_index)

    def _set_property_view_index(self, index):
        """
        Set proprty_table_view model to node property model.
        """

        self._property_widget.set_object_index(index)

        return

    def _set_object_connections_index(self, index):
        """
        Set object connections view to index
        """

        self._object_connections_widget.set_root_index(index)

        return

    def _set_property_connections_index(self, index):
        """
        Set property connections view to index
        """

        self._property_connections_widget.set_root_index(index)

        return

    def _clear_selection(self):
        # clear tree selection
        if self._tree_widget.view.selectionModel() is not None:
            self._tree_widget.view.selectionModel().clearSelection()

        # clear property view selection
        # by passing in invalid index
        self._set_property_view_index(
            Qt.QtCore.QModelIndex()
        )

        return True


class Test1(Qt.QtWidgets.QWidget):
    def __init__(self, file_path, parent=None):
        super(Test1, self).__init__(parent=parent)

        self._file_path = file_path

        self._scene, self._fbx_manager = bfIO.load_fbx_file(
            self._file_path,
            fbx_manager=None
        )

        self.create_widgets()
        self.create_layout()

        self.setGeometry(
            Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.1,
            Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.1,
            400,
            800
        )

        self.show()

    def create_widgets(self):
        self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()
        self.scene_model.set_scene(self._scene, self._fbx_manager)

        self.filter_model = bfSceneModels.BFbxSceneDummyFilterModel()
        self.filter_model.setSourceModel(self.scene_model)

        self.scene_widget = BfSceneTreeWidget()
        self.scene_widget.setModel(self.filter_model)

    def create_layout(self):
        self.lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self.lyt)
        self.lyt.addWidget(self.scene_widget)


class Test2(Qt.QtWidgets.QWidget):
    def __init__(self, file_path, parent=None):
        super(Test2, self).__init__(parent=parent)

        self._file_path = file_path

        self._scene, self._fbx_manager = bfIO.load_fbx_file(
            self._file_path,
            fbx_manager=None
        )

        self.model_manager = bfModelManagers.BfSceneModelManager()
        self.model_manager.set_scene(self._scene, self._fbx_manager)

        self.create_widgets()
        self.create_layout()

        self.setGeometry(
            Qt.QtWidgets.QApplication.desktop().screenGeometry().width() * 0.1,
            Qt.QtWidgets.QApplication.desktop().screenGeometry().height() * 0.1,
            800,
            800
        )

        self.show()

    def create_widgets(self):
        #         self.scene_model = bfSceneModels.BFbxSceneTreeQtModel()
        #         self.scene_model.set_scene(self._scene, self._fbx_manager)
        #
        #         self.filter_model = bfSceneModels.BFbxSceneDummyFilterModel()
        #         self.filter_model.setSourceModel(self.scene_model)

        self.scene_widget = BFbxSceneWidget()

        self.scene_widget.set_model_manager(self.model_manager)

#         self.scene_widget.set_scene_model(
#             self.model_manager.scene_filter_model()
#         )

    def create_layout(self):
        self.lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self.lyt)
        self.lyt.addWidget(self.scene_widget)


if __name__ == "__main__":

    DUMP_DIR = r"D:\Repos\dataDump\brenrig"
#     TEST_FILE = "fbx_scene_sorting_example_01.fbx"
    TEST_FILE = "fbx_property_hierarchy_test_01.fbx"

    app = Qt.QtWidgets.QApplication(sys.argv)

    if False:
        test = Test1(
            os.path.join(DUMP_DIR, TEST_FILE)
        )
    elif False:
        dialog = BFbxTypeSelectionDialog()
        dialog.setModal(True)  # or setWindowModality()
        dialog.show()
    elif False:
        view = BFbxClassIdBoolView()
        model = bfDataModels.BFbxClassIdBoolTreeModel()
        view.setModel(model)
        view.expandAll()
        view.show()
    elif True:
        test = Test2(
            os.path.join(DUMP_DIR, TEST_FILE)
        )

    sys.exit(app.exec_())
