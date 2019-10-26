"""
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
from brenpy.qt.icons import icons8

from brenfbx.core import bfIO
from brenfbx.core import bfUtils
from brenfbx.core import bfCore
from brenfbx.core import bfProperty
from brenfbx.core import bfObject

from brenfbx.qt import bfQtWidgets
from brenfbx.qt import bfQtCache


class BfEditMenu(Qt.QtWidgets.QMenu):
    """Edit menu
    """

    def __init__(self, parent=None):
        super(BfEditMenu, self).__init__(parent)

        self.setTitle("Edit")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        self.undo_action = Qt.QtWidgets.QAction(_icon, 'Undo', self)
#         self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.setStatusTip('Undo last action')

        self.redo_action = Qt.QtWidgets.QAction(_icon, 'Redo', self)
#         self.undo_action.setShortcut('Ctrl+Z')
        self.redo_action.setStatusTip('Redo last action')

        self.cut_action = Qt.QtWidgets.QAction(_icon, 'Cut', self)
#         self.cut_action.setShortcut('Ctrl+X')
        self.cut_action.setStatusTip('Cut selected objects')

        self.copy_action = Qt.QtWidgets.QAction(_icon, 'Copy', self)
#         self.copy_action.setShortcut('Ctrl+C')
        self.copy_action.setStatusTip('Copy selected objects')

        self.paste_action = Qt.QtWidgets.QAction(_icon, 'Paste', self)
#         self.paste_action.setShortcut('Ctrl+V')
        self.paste_action.setStatusTip('Paste clipboard objects')

        self.delete_action = Qt.QtWidgets.QAction(_icon, 'Delete', self)
#         self.del_action.setShortcut('Ctrl+V')
        self.delete_action.setStatusTip('Delete selected objects')

        self.duplicate_action = Qt.QtWidgets.QAction(_icon, 'Duplicate', self)
#         self.dup_action.setShortcut('Ctrl+D')
        self.duplicate_action.setStatusTip('Duplicate selected objects')

        self.group_action = Qt.QtWidgets.QAction(_icon, 'Group', self)
#         self.group_action.setShortcut('Ctrl+G')
        self.group_action.setStatusTip('Group selected objects')

        self.parent_action = Qt.QtWidgets.QAction(_icon, 'Parent', self)
#         self.group_action.setShortcut('Ctrl+G')
        self.parent_action.setStatusTip(
            'Parent selected nodes to last selected node')

        self.unparent_action = Qt.QtWidgets.QAction(_icon, 'Unparent', self)
#         self.group_action.setShortcut('Ctrl+G')
        self.unparent_action.setStatusTip('Unparent selected nodes')

    def _add_actions(self):

        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addSeparator()
        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addSeparator()
        self.addAction(self.delete_action)
        self.addAction(self.duplicate_action)
        self.addSeparator()
        self.addAction(self.group_action)
        self.addAction(self.parent_action)
        self.addAction(self.unparent_action)


class BFbxClassIdBoolMenu(Qt.QtWidgets.QMenu):
    """Actions for selecting and checking items.
    """

    def __init__(self, parent=None):
        super(BFbxClassIdBoolMenu, self).__init__(parent)

        self.setTitle("Select")
        self._create_actions()
        self._add_actions()

    def _create_actions(self):
        """TODO icons
        """

        _icon = Qt.QtGui.QIcon()

        self.select_all = Qt.QtWidgets.QAction(_icon, 'Select all', self)
        self.deselect_all = Qt.QtWidgets.QAction(_icon, 'Deselect all', self)

        self.check_all = Qt.QtWidgets.QAction(_icon, 'Check all', self)
        self.uncheck_all = Qt.QtWidgets.QAction(_icon, 'Uncheck all', self)
        self.toggle_all = Qt.QtWidgets.QAction(_icon, 'Toggle all', self)

        self.check_selected = Qt.QtWidgets.QAction(
            _icon, 'Check selected', self
        )

        self.uncheck_selected = Qt.QtWidgets.QAction(
            _icon, 'Uncheck selected', self
        )

        self.toggle_selected = Qt.QtWidgets.QAction(
            _icon, 'Toggle selected', self
        )

        self.import_data = Qt.QtWidgets.QAction(_icon, 'Import data', self)
        self.export_data = Qt.QtWidgets.QAction(_icon, 'Export data', self)

    def _add_actions(self):

        self.addAction(self.select_all)
        self.addAction(self.deselect_all)
        self.addSeparator()
        self.addAction(self.check_all)
        self.addAction(self.uncheck_all)
        self.addAction(self.toggle_all)
        self.addSeparator()
        self.addAction(self.check_selected)
        self.addAction(self.uncheck_selected)
        self.addAction(self.toggle_selected)
        self.addSeparator()
        self.addAction(self.export_data)
        self.addAction(self.import_data)
