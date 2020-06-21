'''
Created on 4 Aug 2019

@author: Bren

** WIP **

'''


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

from brenfbx.core import bfIO

from brenrig.sandbox.fbx_prototype_01 import brSession
from brenrig.sandbox.fbx_prototype_01 import brQtSsession
from brenrig.sandbox.fbx_prototype_01 import test_scene_02


DEFAULT_LABEL_WIDTH = 50


class HierarchySortFitler(Qt.QtCore.QSortFilterProxyModel):
    """Allows parents of filtered row to remain visible.

    https://stackoverflow.com/questions/250890/using-qsortfilterproxymodel-with-a-tree-model

    ** WIP **
    """

    HIGHLIGHT_COLOR = Qt.QtGui.QColor(200, 225, 255)

    def __init__(self, *args, **kwargs):
        super(HierarchySortFitler, self).__init__(*args, **kwargs)

        self.setFilterKeyColumn(0)

        self._highlighted_indices = set([])

    def data(self, index, role):
        """Override source model data method.

        Add background colour for highlited indices.
        """

        if not index.isValid():
            return

        if role == Qt.QtCore.Qt.BackgroundRole:
            # TODO use uniqueID instead of name??

            #             GetUniqueID
            #             node = index.internalPointer()
            #             print node
            #             name = self.sourceModel().data(index, Qt.QtCore.Qt.DisplayRole)
            #             print name

            name = super(HierarchySortFitler, self).data(
                index, Qt.QtCore.Qt.DisplayRole
            )

            if name in self._highlighted_indices:
                return self.HIGHLIGHT_COLOR

        else:
            return super(HierarchySortFitler, self).data(index, role)

    def filterAcceptsRow(self, source_row, source_parent):
        # custom behaviour
        if not self.filterRegExp().isEmpty():
            # get source model index for current row
            source_index = self.sourceModel().index(
                source_row, self.filterKeyColumn(), source_parent)

            if source_index.isValid():
                # check current index
                key = self.sourceModel().data(source_index, self.filterRole())
                match = self.filterRegExp().exactMatch(key)

                if match:
                    name = self.sourceModel().data(source_index, Qt.QtCore.Qt.DisplayRole)
                    self._highlighted_indices.add(name)

                # if any of children matches the filter, then current index
                # matches the filter as well

                row_count = self.sourceModel().rowCount(source_index)

                for i in range(row_count):
                    if self.filterAcceptsRow(i, source_index):
                        return True

                # return current match
                return match

        # parent call for default behaviour
        return super(HierarchySortFitler, self).filterAcceptsRow(source_row, source_parent)

#     def set_fbx_scene(self, fbx_scene):
#         self.sourceModel().set_fbx_scene(fbx_scene)
#         self.update()

    def set_session(self, session_object):
        self.sourceModel().set_session(session_object)
        self.update()

    def update(self):
        self.sourceModel().update()


class LabeledLineEditWidget(Qt.QtWidgets.QWidget):
    """Simple widget with a label and lineEdit widgets."""

    def __init__(self, label, parent=None):
        super(LabeledLineEditWidget, self).__init__(parent)

        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.label = Qt.QtWidgets.QLabel(label)
        self.edit = Qt.QtWidgets.QLineEdit()

        self.label.setMinimumWidth(50)

        self.lyt.addWidget(self.label)
        self.lyt.addWidget(self.edit)

        self.setLayout(self.lyt)


class InspectorWidget(Qt.QtWidgets.QWidget):
    """Test widget to mimic maya channel box or unity inspector.
    ** WIP **
    """

    def __init__(self, parent=None):
        super(InspectorWidget, self).__init__(parent)

        self.data_mapper = Qt.QtWidgets.QDataWidgetMapper()

        self.lyt = Qt.QtWidgets.QVBoxLayout()

        # hard code a couple of property widgets
        self.name_widget = LabeledLineEditWidget("name")
        self.name_widget.setEnabled(False)

        # temp
        self.type_widget = LabeledLineEditWidget("type")
        self.type_widget.edit.setReadOnly(True)
        self.type_widget.setEnabled(False)

        self.lyt.addWidget(self.name_widget)
        self.lyt.addWidget(self.type_widget)

        self.setLayout(self.lyt)

    # if using a regular model
    def setModel(self, model):
        self.model = model

        # create widget mapping
        self.data_mapper.setModel(self.model)

    # if using a proxy model for sorting/filtering etc
    def setProxyModel(self, proxy_model):
        self._proxy_model = proxy_model
        self.setModel(proxy_model.sourceModel())

    def add_mapping(self):
        # mapping(widget, column)
        self.data_mapper.addMapping(self.name_widget.edit, 0)
        self.data_mapper.addMapping(self.type_widget.edit, 1)

        # bind mapper to first row in model
#         self.data_mapper.toFirst()

    def setSelection(self, index, old_index):
        if index.isValid():
            self.add_mapping()
            self.data_mapper.setRootIndex(index.parent())
            self.data_mapper.setCurrentModelIndex(index)
            self.name_widget.setEnabled(True)
            self.type_widget.setEnabled(True)
        else:
            self.data_mapper.clearMapping()
            self.name_widget.edit.setText(None)
            self.name_widget.setEnabled(False)
            self.type_widget.edit.setText(None)
            self.type_widget.setEnabled(False)


class BrFileMenu(Qt.QtWidgets.QMenu):
    """File menu
    """

    def __init__(self, parent=None):
        super(BrFileMenu, self).__init__(parent)

        self.setTitle("File")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        # new menu item/ shortcut
        self.new_action = Qt.QtWidgets.QAction(Qt.QtGui.QIcon(), 'New', self)
        self.new_action.setShortcut('Ctrl+N')
        self.new_action.setStatusTip('New scene')

        # open menu item/ shortcut
        open_icon = self.style().standardIcon(
            Qt.QtWidgets.QStyle.SP_DialogOpenButton
        )

        self.open_action = Qt.QtWidgets.QAction(open_icon, 'Open', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.setStatusTip('Open fbx file')

        # import TODO
#         import_icon = self.style().standardIcon(
#             Qt.QtWidgets.QStyle.SP_DialogOpenButton
#         )

        self.import_action = Qt.QtWidgets.QAction(
            Qt.QtGui.QIcon(), 'Import', self)
        # TODO check what this should be
        self.import_action.setShortcut('Ctrl+I')
        self.import_action.setStatusTip('Import fbx file')

        # merge TODO
        self.merge_action = Qt.QtWidgets.QAction(
            Qt.QtGui.QIcon(), 'Merge', self)
        # TODO check what this should be
        self.merge_action.setShortcut('Ctrl+Shift+I')
        self.merge_action.setStatusTip('Merge fbx file')

        # save
        save_icon = self.style().standardIcon(
            Qt.QtWidgets.QStyle.SP_DialogSaveButton
        )

        self.save_action = Qt.QtWidgets.QAction(save_icon, 'Save', self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.setStatusTip('Save fbx file')

        # save as
        self.save_as_action = Qt.QtWidgets.QAction(save_icon, 'Save As', self)
        self.save_as_action.setShortcut('Ctrl+Shift+S')
        self.save_as_action.setStatusTip('Save as fbx file')

        # exit
        self.exit_action = Qt.QtWidgets.QAction(
            Qt.QtGui.QIcon(), 'Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')

    def _add_actions(self):

        self.addAction(self.new_action)
        self.addAction(self.open_action)
        self.addAction(self.import_action)
        self.addAction(self.merge_action)
        self.addAction(self.save_action)
        self.addAction(self.save_as_action)
        self.addAction(self.exit_action)


class BrCreateMenu(Qt.QtWidgets.QMenu):
    """Create menu
    """

    def __init__(self, parent=None):
        super(BrCreateMenu, self).__init__(parent)

        self.setTitle("Create")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        # new menu item/ shortcut
        self.guide_loc_action = Qt.QtWidgets.QAction(
            _icon, 'Guide Locator', self)
        self.guide_loc_action.setStatusTip('New guide locator')

        # joint
        self.joint_action = Qt.QtWidgets.QAction(_icon, 'Joint', self)
        self.joint_action.setStatusTip('New joint')

        # modifiers and sub menu
        self.modifier_action = Qt.QtWidgets.QAction(_icon, 'Modifier', self)
        self.modifier_action.setStatusTip('New modifier')

        # modifiers and sub menu
        self.build_action = Qt.QtWidgets.QAction(_icon, 'Build', self)
        self.build_action.setStatusTip('New build')

    def _add_actions(self):

        self.addAction(self.guide_loc_action)
        self.addAction(self.joint_action)
        self.addAction(self.modifier_action)
        self.addAction(self.build_action)


class BrEditMenu(Qt.QtWidgets.QMenu):
    """Edit menu
    """

    def __init__(self, parent=None):
        super(BrEditMenu, self).__init__(parent)

        self.setTitle("Edit")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        self.undo_action = Qt.QtWidgets.QAction(_icon, 'Undo', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.setStatusTip('Undo last action')

        self.redo_action = Qt.QtWidgets.QAction(_icon, 'Redo', self)
#         self.undo_action.setShortcut('Ctrl+Z')
        self.redo_action.setStatusTip('Redo last action')

        self.cut_action = Qt.QtWidgets.QAction(_icon, 'Cut', self)
        self.cut_action.setShortcut('Ctrl+X')
        self.cut_action.setStatusTip('Cut selected objects')

        self.copy_action = Qt.QtWidgets.QAction(_icon, 'Copy', self)
        self.copy_action.setShortcut('Ctrl+C')
        self.copy_action.setStatusTip('Copy selected objects')

        self.paste_action = Qt.QtWidgets.QAction(_icon, 'Paste', self)
        self.paste_action.setShortcut('Ctrl+V')
        self.paste_action.setStatusTip('Paste clipboard objects')

        self.del_action = Qt.QtWidgets.QAction(_icon, 'Delete', self)
#         self.del_action.setShortcut('Ctrl+V')
        self.del_action.setStatusTip('Delete selected objects')

        self.dup_action = Qt.QtWidgets.QAction(_icon, 'Duplicate', self)
        self.dup_action.setShortcut('Ctrl+D')
        self.dup_action.setStatusTip('Duplicate selected objects')

        self.group_action = Qt.QtWidgets.QAction(_icon, 'Group', self)
        self.group_action.setShortcut('Ctrl+G')
        self.group_action.setStatusTip('Group selected objects')

    def _add_actions(self):

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addSeparator()
        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addSeparator()
        self.addAction(self.del_action)
        self.addAction(self.dup_action)
        self.addAction(self.group_action)


class BrDccMenu(Qt.QtWidgets.QMenu):
    """DCC menu
    TODO
    """

    def __init__(self, parent=None):
        super(BrDccMenu, self).__init__(parent)

        self.setTitle("DCC")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        self.create_guides_action = Qt.QtWidgets.QAction(
            _icon, 'Create guides', self)
#         self.undo_action.setShortcut('Ctrl+Z')
        self.create_guides_action.setStatusTip(
            'Create guide objects in DCC scene')

    def _add_actions(self):

        self.addAction(self.create_guides_action)


class BrTaskMenu(Qt.QtWidgets.QMenu):
    """Task menu
    TODO
    """

    def __init__(self, parent=None):
        super(BrTaskMenu, self).__init__(parent)

        self.setTitle("Task")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        self.build_action = Qt.QtWidgets.QAction(_icon, 'Build', self)
#         self.undo_action.setShortcut('Ctrl+Z')
        self.build_action.setStatusTip('Evaluate a build object')
        # TODO build widget, showing a list of available build objects to build
        # with current context highlighted (if applicable)

        self.publish_action = Qt.QtWidgets.QAction(_icon, 'Publish', self)
#         self.undo_action.setShortcut('Ctrl+Z')
        self.publish_action.setStatusTip('Evaluate a publish object')

        # TODO publish widget with current context highlighted (if applicable)
        # publish context might be found in the dcc scene

    def _add_actions(self):

        self.addAction(self.build_action)
        self.addAction(self.publish_action)


class BrMappedWidget(Qt.QtWidgets.QWidget):
    """Stuff"""

    def __init__(self, parent=None):
        super(BrMappedWidget, self).__init__(parent)

        self._mapped = False

        self._data_mapper = Qt.QtWidgets.QDataWidgetMapper()

        self.setFixedHeight(20)

        self._create_widgets()
        self._create_layout()

    def _create_widgets(self):
        pass

    def _create_layout(self):
        pass

    def setModel(self, model):
        self.model = model

        self._data_mapper.setModel(self.model)
#         self.map_to_index()

    def add_mappings(self):
        pass
#         self.data_mapper.toFirst()

    def setSelection(self, index):
        if not index.isValid():
            self.clear()
            return

        if not self._mapped:
            self.add_mappings()
            self._mapped = True

        self._data_mapper.setRootIndex(index.parent())
        self._data_mapper.setCurrentModelIndex(index)

    def clear(self):
        self._data_mapper.clearMapping()
        self._mapped = False
        self.clear_widgets()

    def clear_widgets(self):
        pass

    def get_current_index(self):
        parent_index = self._data_mapper.rootIndex()
        row = self._data_mapper.currentIndex()
        index = self.model.index(row, 0, parent_index)
        return index


class BrObjectNameWidget(BrMappedWidget):
    """Stuff
    TODO if index is not editable, set line edit to be not editable.
    """

    def __init__(self, parent=None):
        super(BrObjectNameWidget, self).__init__(parent)

    def _create_widgets(self):
        self._label = Qt.QtWidgets.QLabel("Name")
        self._line_edit = Qt.QtWidgets.QLineEdit()
        self._label.setFixedWidth(DEFAULT_LABEL_WIDTH)
        self._line_edit.setEnabled(False)

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.lyt.setContentsMargins(0, 0, 0, 0)
#         self.lyt.setSpacing(5)

        self.lyt.addWidget(self._label)
        self.lyt.addWidget(self._line_edit)
        self.setLayout(self.lyt)

    def add_mappings(self):
        self._line_edit.setEnabled(True)
        self._data_mapper.addMapping(self._line_edit, 0)
        self._data_mapper.toFirst()

    def clear_widgets(self):
        self._line_edit.setText("")
        self._line_edit.setEnabled(False)


class BrObjectTypeWidget(BrMappedWidget):
    """Stuff"""

    def __init__(self, parent=None):
        super(BrObjectTypeWidget, self).__init__(parent)

    def _create_widgets(self):
        self.type_label = Qt.QtWidgets.QLabel("Type")
        self.pixmap_label = Qt.QtWidgets.QLabel()
        self.text_label = Qt.QtWidgets.QLabel()
        self.type_label.setFixedWidth(DEFAULT_LABEL_WIDTH)
        self.pixmap_label.setFixedWidth(20)

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.lyt.setContentsMargins(0, 0, 0, 0)
#         self.lyt.setSpacing(5)

        self.lyt.addWidget(self.type_label)
        self.lyt.addWidget(self.pixmap_label)
        self.lyt.addWidget(self.text_label)
        self.setLayout(self.lyt)

    def add_mappings(self):
        self._data_mapper.addMapping(self.pixmap_label, 2, "pixmap")
        self._data_mapper.addMapping(self.text_label, 1, "text")

    def clear_widgets(self):
        self.text_label.setText("")
        self.pixmap_label.setPixmap(None)


class BrSessionTreeView(Qt.QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super(BrSessionTreeView, self).__init__(parent)

        self.setIndentation(10)

        self.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )


class BFbxEditor(Qt.QtWidgets.QMainWindow):

    USE_FILTER = True
    USE_CUSTOM_FILTER = True
    USE_INSPECTOR = True

    def __init__(self, parent=None, file_path=None):
        super(BFbxEditor, self).__init__(parent)

        self._filter_value = ""

        self._debug_print = True

        self._file_path = file_path
        self._default_path = None

        self._fbx_manager = None
        self._fbx_scene = None
        self._session = None

        # create qt objects
        self.setCentralWidget(
            Qt.QtWidgets.QWidget()
        )

        self._create_widgets()
        self._create_layout()
        self._create_model()

        self._create_menus()
        self._create_menu_bar()
        self._create_status_bar()

        self._connect_widgets()

        # if file is given, load it!
        if file_path is not None:
            self._load_fbx()
        else:
            self._new_session()

    def debug(self, msg):
        '''
        print in context
        # TODO proper logging
        '''

        if self._debug_print:
            print msg

        # convert msg to something readable on status bar
        msg = str(msg)
        self.status_bar.showMessage(msg)

    def _destroy_fbx_objects(self):
        """Destroy fbx manager and fbx scene.
        Ensures references are clean ready for new scene.
        """
        if self._fbx_manager is not None:
            self._fbx_manager.Destroy()
            self._fbx_manager = None

        if self._fbx_scene is not None:
            self._fbx_scene.Destroy()
            self._fbx_scene = None

    def _update_fbx_scene(self):
        """
        TODO do we actually need to keep a reference to the scene?
        """
        if self._session is None:
            return

        self._fbx_scene = self._session.Scene()

    def _new_session(self):
        # clear selections to clear all connected widgets etc.
        self._clear_selection()

        # inform Qt objects we are about to change the scene
        self.model.beginResetModel()

        # clear old objects
#         self._destroy_fbx_objects()

        # make new objects
        self._session, self._fbx_manager = brSession.BrSession.New(
            fbx_manager=self._fbx_manager,
            fbx_scene=None
        )
#         self._update_fbx_scene()

        self._file_path = None

        # inform Qt objects we are done changing the scene
        self.model.set_session(self._session)
        self.model.endResetModel()

        self._session_tree.expandAll()

        # set title
        self._update_title()

    def _update_title(self):
        if self._file_path is not None:
            title = self._file_path
        else:
            title = "untitled session"

        self.setWindowTitle(title)

    def _update_default_path(self):
        if self._file_path is not None:
            self._default_path = os.path.dirname(self._file_path)
        else:
            self._default_path = None

    def _load_fbx(self):
        # clear selections to clear all connected widgets etc.
        self._clear_selection()

        # inform Qt objects we are about to change the scene
        self.model.beginResetModel()

        # clear old objects
#         self._destroy_fbx_objects()

        # create session
        self._session, self._fbx_manager = bfIO.load_fbx_file(
            self._file_path,
            fbx_manager=self._fbx_manager
        )

#         self._update_fbx_scene()

        # inform Qt objects we are done changing the scene
        self.model.set_session(self._session)
        self.model.endResetModel()

        self._session_tree.expandAll()

        # set title
        self._update_title()
        self._update_default_path()
#         if self.USE_CUSTOM_FILTER:
#             self._proxy_model.set_fbx_scene(self._fbx_scene)
# #             self._proxy_model.update()
#         else:
#             self.model.set_fbx_scene(self._fbx_scene)
# #             self.model.update()

    def _save_fbx_file(self):
        self._session.Save(
            self._fbx_manager,
            self._file_path,
            overwrite=True
        )

        self._update_title()
        self._update_default_path()

    def _create_menus(self):
        self._create_file_menu()
        self._create_create_menu()
        self._create_edit_menu()
        self._create_dcc_menu()
        self._create_task_menu()

    def _create_menu_bar(self):
        """Create menu bar and add menus.
        """
        self.menubar = self.menuBar()
        self.menubar.addMenu(self._file_menu)
        self.menubar.addMenu(self._edit_menu_widget)
        self.menubar.addMenu(self._create_menu_widget)
        self.menubar.addMenu(self._dcc_menu_widget)
        self.menubar.addMenu(self._task_menu_widget)

    def _create_file_menu(self):
        """Create and connect File menu.
        """
        self._file_menu = BrFileMenu(self)

        # connect menu
        self._file_menu.new_action.triggered.connect(
            self._new_session
        )

        self._file_menu.open_action.triggered.connect(
            self._open_fbx_file_dialog
        )

        self._file_menu.save_as_action.triggered.connect(
            self._save_as_fbx_file_dialog
        )

        self._file_menu.exit_action.triggered.connect(
            Qt.QtWidgets.QApplication.instance().quit
        )

    def _create_create_menu(self):
        """Create and connect Create menu.
        """
        self._create_menu_widget = BrCreateMenu(self)

        # connect menu
        self._create_menu_widget.guide_loc_action.triggered.connect(
            self._create_guide
        )

        self._create_menu_widget.joint_action.triggered.connect(
            self._create_joint
        )

        self._create_menu_widget.build_action.triggered.connect(
            self._create_build
        )

    def _create_edit_menu(self):
        """Create and connect edit menu.
        """
        self._edit_menu_widget = BrEditMenu(self)

        # connect menu
        self._edit_menu_widget.del_action.triggered.connect(
            self._delete_selected
        )

    def _create_dcc_menu(self):
        """Create and connect dcc menu.
        """
        self._dcc_menu_widget = BrDccMenu(self)

        # connect menu
#         self._create_menu_widget.new_action.triggered.connect(
#             self._new_session
#         )

    def _create_task_menu(self):
        """Create and connect task menu.
        """
        self._task_menu_widget = BrTaskMenu(self)

        # connect menu
#         self._create_menu_widget.new_action.triggered.connect(
#             self._new_session
#         )

    def _create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

    def _open_fbx_file_dialog(self):
        file_path, file_type = Qt.QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open file',
            self._default_path,
            "fbx files (*.fbx)"
        )

        if file_path == "":
            return

        self.debug(file_path)

        if os.path.exists(file_path):
            self._file_path = file_path
            self._load_fbx()
#             self._update_data()

    def _save_as_fbx_file_dialog(self):
        file_path, file_type = Qt.QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Save file',
            self._file_path or self._default_path,
            "Fbx files (*.fbx)"
        )

        if file_path == "":
            return

        self.debug("Attempting to save file: {}".format(file_path))

        if os.path.exists(file_path):
            self.debug(['overwriting ', file_path])

        old_file_path = str(self._file_path)

        self._file_path = file_path

        try:
            self._save_fbx_file()
            self.debug("File saved as: {}".format(file_path))
        except:  # something?
            self.debug("Failed to save as: {}".format(file_path))
            self._file_path = old_file_path
            raise

    def _create_widgets(self):
        """
        table view selection/edit options:
        https://stackoverflow.com/questions/18831242/qt-start-editing-of-cell-after-one-click

        Constant    Value   Description
        QAbstractItemView::NoEditTriggers   0   No editing possible.
        QAbstractItemView::CurrentChanged   1   Editing start whenever current item changes.
        QAbstractItemView::DoubleClicked    2   Editing starts when an item is double clicked.
        QAbstractItemView::SelectedClicked  4   Editing starts when clicking on an already selected item.
        QAbstractItemView::EditKeyPressed   8   Editing starts when the platform edit key has been pressed over an item.
        QAbstractItemView::AnyKeyPressed    16  Editing starts when any key is pressed over an item.
        QAbstractItemView::AllEditTriggers  31  Editing starts for all above actions.

        """
        # tree filter
        self.filter_box = Qt.QtWidgets.QLineEdit()

        # object selection tree
        if False:
            self.tree = Qt.QtWidgets.QTreeView()
            self.tree.setIndentation(10)
            self.tree.setSelectionMode(
                Qt.QtWidgets.QAbstractItemView.ExtendedSelection
            )

        else:
            self._session_tree = BrSessionTreeView()

        # property table
#         self.property_table_view = Qt.QtWidgets.QTableView(self)
        self.property_tree_view = Qt.QtWidgets.QTreeView(self)

        # property edit deligate
        self.property_deligate = brQtSsession.PropertyFnStrDeligate(
            self.property_tree_view
        )

#         self.property_table_view.setItemDelegate(
#             self.property_deligate
#         )
        self.property_tree_view.setItemDelegate(
            self.property_deligate
        )

#         self.property_table_view.setEditTriggers(
#             Qt.QtWidgets.QAbstractItemView.AllEditTriggers
#         )

        # inspector
        self._object_name_widget = BrObjectNameWidget()
        self._object_type_widget = BrObjectTypeWidget()

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout(self.centralWidget())

        self.lyt_splitter = Qt.QtWidgets.QSplitter()
#         self.lyt_splitter.setHandleWidth(1)
#         self.lyt_splitter.setRubberBand(100)

        self.hierarchy_widget = Qt.QtWidgets.QWidget()
        self.hierarchy_lyt = Qt.QtWidgets.QVBoxLayout()
        self.hierarchy_widget.setLayout(self.hierarchy_lyt)

        self.object_editor_widget = Qt.QtWidgets.QWidget()
        self.object_editor_lyt = Qt.QtWidgets.QVBoxLayout()
        self.object_editor_widget.setLayout(self.object_editor_lyt)

        self.lyt_splitter.addWidget(self.hierarchy_widget)
        self.lyt_splitter.addWidget(self.object_editor_widget)

        self.lyt_splitter.setSizes([50, 100])

        self.lyt.addWidget(self.lyt_splitter)

#         self.lyt.addLayout(self.hierarchy_lyt)
#         self.lyt.addLayout(self.property_lyt)

        # tree
        self.hierarchy_lyt.addWidget(self.filter_box)
        self.hierarchy_lyt.addWidget(self._session_tree)

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

        self._name_type_lyt = Qt.QtWidgets.QVBoxLayout(self._name_type_frame)
#         self._name_type_lyt.setContentsMargins(5, 5, 5, 5)
#         self._name_type_lyt.setSpacing(5)

        self.object_editor_lyt.addWidget(self._name_type_frame)

        self._name_type_lyt.addWidget(self._object_name_widget)
        self._name_type_lyt.addWidget(self._object_type_widget)

        # property widgets

        self._property_frame = Qt.QtWidgets.QFrame()

        self._property_frame.setFrameStyle(
            Qt.QtWidgets.QFrame.StyledPanel | Qt.QtWidgets.QFrame.Sunken
            #             QtGui.QFrame.Panel | QtGui.QFrame.Raised
        )

        self._property_frame.setLineWidth(1)
        self._property_lyt = Qt.QtWidgets.QVBoxLayout(self._property_frame)

        self._property_lyt.addWidget(self.property_tree_view)

        self.object_editor_lyt.addWidget(self._property_frame)

    def _create_model(self):
        """Create fbx scene model and filters.
        """

        self.model = brQtSsession.BrSessionQtModel(self)

        self._proxy_model = HierarchySortFitler()

        self._proxy_model.setFilterCaseSensitivity(
            Qt.QtCore.Qt.CaseSensitivity.CaseInsensitive
        )

        self._proxy_model.setSourceModel(self.model)

#         self._tree_to_list_model = bpQtCore.BpItemToListProxyModel()
#         self._tree_to_list_model.setSourceModel(self.model)

        # set our custom role enum to be called when sending sortRole to
        # things
#             self._proxy_model.setSortRole(FbxSceneQtModel.kSortRole)
#             self._proxy_model.setFilterRole(FbxSceneQtModel.kFilterRole)

    def _connect_widgets(self):

        self._session_tree.setModel(self._proxy_model)
#         self._session_tree.setModel(self.model)
        self.filter_box.textChanged.connect(self._filter_edit_changed)

        if True:
            # TESTING
            self._completer = Qt.QtWidgets.QCompleter()
            self._completer.setModel(self.model)
            self._completer.setCaseSensitivity(
                Qt.QtCore.Qt.CaseSensitivity.CaseInsensitive)
            self.filter_box.setCompleter(self._completer)

        # connect object selection
        Qt.QtCore.QObject.connect(
            self._session_tree.selectionModel(),
            SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
            self._tree_current_changed
        )

        Qt.QtCore.QObject.connect(
            self._session_tree.selectionModel(),
            SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
            self._tree_selection_changed
        )

        # connect mapped widgets
        self._object_name_widget.setModel(self.model)
        self._object_type_widget.setModel(self.model)

    def _tree_selection_changed(self, new_selected, new_deselected):
        """Update widgets with multiple or empty index selections.
        Normally called before self._tree_current_changed().
        """
        selected = self._session_tree.selectionModel().selection()

#         print "selection changed"

        if len(selected):
            # get last selected index
            #             index = selected.indexes()[-1]
            index = self._session_tree.selectionModel().currentIndex()
            index = self._proxy_model.mapToSource(index)
# #                 old_index = self._proxy_model.mapToSource(old_index)
#
#
#             if self.USE_INSPECTOR:
#                 self.inspector_widget.setSelection(index, None)
        else:
            # set invalid index to indicate empty selection
            index = Qt.QtCore.QModelIndex()

#             self._set_property_table_view_index(invalid_index, None)

        for widget in [
            self._object_name_widget,
            self._object_type_widget
        ]:
            widget.setSelection(index)

        self._set_property_view_index(index)

    def _tree_current_changed(self, index, old_index):
        """Update corresponding widgets to current selected index.
        Normally called after self._tree_selection_changed().
        """

        src_index = self._proxy_model.mapToSource(index)
        src_old_index = self._proxy_model.mapToSource(old_index)

        self._set_property_view_index(src_index)

#         print "current changed"

        for widget in [
            self._object_name_widget,
            self._object_type_widget
        ]:
            widget.setSelection(src_index)

    def _filter_edit_changed(self):
        # get filter value
        value = self.filter_box.text()

        # reset highlighted indices and set new filter
        if self.USE_CUSTOM_FILTER:
            self._proxy_model._highlighted_indices.clear()

        # use wildcards either side for convinience
        if value != "":
            value = "*{}*".format(value)

        self._proxy_model.setFilterWildcard(value)

        # show all results
        # TODO change this to only expand to matching results
        self._session_tree.expandAll()

    def _set_property_view_index(self, index):
        """
        Set proprty_table_view model to node property model.
        """
        if not index.isValid():
            prop_model = None

        else:
            br_object = self.model.get_br_object(index)
            node_id = br_object.GetUniqueID()

            if node_id in self.model._property_list_models.keys():
                prop_model = self.model._property_list_models[node_id]
            else:
                prop_model = None

#         print "setting prop table model: {}".format(prop_model)
#         self.property_table_view.setModel(prop_model)
        print "setting prop tree model: {}".format(prop_model)
        self.property_tree_view.setModel(prop_model)
        self.property_tree_view.expandAll()

        return

    def _clear_selection(self):
        # clear tree selection
        if self._session_tree.selectionModel() is not None:
            self._session_tree.selectionModel().clearSelection()

        # clear property view selection
        # by passing in invalid index
        self._set_property_view_index(
            Qt.QtCore.QModelIndex()
        )

        return True

    def _delete_selected(self):
        """TODO maintain how tree is currently expanded.
        """
        if self._session_tree.selectionModel() is None:
            print "nothing selected"
            return

        selected = self._session_tree.selectionModel().selection()

        self._clear_selection()

        indices_to_delete = []

        for proxy_index in selected.indexes():
            index = self._proxy_model.mapToSource(proxy_index)
            indices_to_delete.append(index)
#             self.model.removeRow(index.row(), index.parent())

        self.model.removeIndices(indices_to_delete)

        self._session_tree.expandAll()

    def _create_guide(self):
        self.model.beginResetModel()

        self._session.create_guide(
            None, None, self._fbx_manager, parent=None
        )

        self.model.reset_model()
        self.model.endResetModel()

        self._session_tree.expandAll()

    def _create_joint(self):
        self.model.beginResetModel()

        self._session.create_joint(None, self._fbx_manager)

        self.model.reset_model()
        self.model.endResetModel()

        self._session_tree.expandAll()

    def _create_build(self):
        self.model.beginResetModel()

        self._session.create_build(None, self._fbx_manager)

        self.model.reset_model()
        self.model.endResetModel()

        self._session_tree.expandAll()

    def _create_br_object(self):
        """
        TODO: how to best select from a range of object types?
        """
        self._session_tree.expandAll()

#     def destroy(self, *args, **kwargs):
#         """Never run?"""
#         # destroy fbx objects
#         self._fbx_manager.Destroy()
#         del self._fbx_manager  # , fbx_scene
#
#         return Qt.QtWidgets.QWidget.destroy(self, *args, **kwargs)


if __name__ == "__main__":
    #     test = brQtSsession.BrIdData(init_value=3.0)
    #     print test.value()

    #     print fbx_modifier_prototype_005.brBox.MdAim.__bases__[0].__bases__[0].__bases__
    #     raise

    app = Qt.QtWidgets.QApplication(sys.argv)

    test_scene_02.export_session_prototype()

    gui = BrEditor(file_path=test_scene_02.TEST_SESSION_FILEPATH)
    gui.show()

    sys.exit(app.exec_())
