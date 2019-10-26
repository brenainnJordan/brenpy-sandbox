'''

TODO
refactor from bren rig prototype

Instead of 

'''

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
from brenfbx.core import bfData
from brenfbx.core import bfProperty
from brenfbx.core import bfObject

from brenfbx.qt import bfQtWidgets
from brenfbx.qt import bfPropertyQtCache
from brenfbx.qt import bfIcons


class CustomCompleter(Qt.QtWidgets.QCompleter):
    def __init__(self, *args, **kwargs):
        super(CustomCompleter, self).__init__(*args, **kwargs)

#         print self.filterMode

#         self.setFilterMode(
#             Qt.QtCore.Qt.MatchContains
#         )

#         return QtGui.QCompleter.__init__(self)

    def splitPath(self, path):
        return path.split(".")

    def pathFromIndex(self, completer_index):
        filter_index = self.completionModel().mapToSource(completer_index)

        filter_model = filter_index.model()

        list_index = filter_model.mapToSource(filter_index)

        list_model = list_index.model()

        src_index = list_model.mapToSource(list_index)

        session_model = list_model.sourceModel()

        fbx_object = session_model.get_fbx_object(src_index)

        path_str = str(fbx_object.GetName())

        return path_str


class BfPropertyCompleter(Qt.QtWidgets.QCompleter):
    def __init__(self, *args, **kwargs):
        super(CustomCompleter, self).__init__(*args, **kwargs)

    def splitPath(self, path):
        return path.split(".")

    def pathFromIndex(self, completer_index):
        filter_index = self.completionModel().mapToSource(completer_index)

        filter_model = filter_index.model()

        list_index = filter_model.mapToSource(filter_index)

        list_model = list_index.model()

        src_index = list_model.mapToSource(list_index)

        session_model = list_model.sourceModel()

        fbx_object = session_model.get_fbx_object(src_index)

        path_str = str(fbx_object.GetName())

        return path_str


class BrInputReferenceDeligateEditor(Qt.QtWidgets.QLineEdit):
    """

    TODO NEEDS REFACTORING

    """

    complete_signal = Qt.QtCore.Signal()

    def __init__(self, parent=None):
        super(BrInputReferenceDeligateEditor, self).__init__(parent)

        self._current_index = Qt.QtCore.QModelIndex()
        self._current_fbx_object = None

        # create completer
        self._completer = CustomCompleter()

        self._completer.setCompletionMode(
            Qt.QtWidgets.QCompleter.UnfilteredPopupCompletion
        )

        self.setCompleter(self._completer)

        self.textEdited.connect(self.text_changed)

    def setSessionModel(self, session_model):
        self.session_model = session_model

        # set completer
        self.list_model = bpQtCore.BpItemToListProxyModel()
        self.list_model.setSourceModel(self.session_model)

        self._filter_model = Qt.QtCore.QSortFilterProxyModel()
        self._filter_model.setFilterCaseSensitivity(
            Qt.QtCore.Qt.CaseInsensitive
        )

        self._filter_model.setSourceModel(self.list_model)

        self._completer.setModel(self._filter_model)

        self.connect_widgets()

    def set_current_index(self, index):
        self._current_index = index

    def current_fbx_object(self):
        return self._current_fbx_object

    def set_current_fbx_object(self, fbx_object):
        self._current_fbx_object = fbx_object

    def completer_activated(self, completer_index):
        print "activated"
        filter_index = self._completer.completionModel().mapToSource(completer_index)
        proxy_index = self._filter_model.mapToSource(filter_index)

        index = self.list_model.mapToSource(proxy_index)

        self.set_current_index(index)

        session_model = index.model()
        fbx_object = session_model.get_fbx_object(index)
        self.set_current_fbx_object(fbx_object)

#         self.setText(fbx_object.GetName())

        self.complete_signal.emit()

    def connect_widgets(self):
        #         self.completer.activated.connect(self.print_test, QtCore.QModelIndex)
        Qt.QtCore.QObject.connect(
            self._completer,
            SIGNAL("activated(QModelIndex)"),
            self.completer_activated
        )

        Qt.QtCore.QObject.connect(
            self._completer,
            SIGNAL("highlighted(QString)"),
            self.test
        )

    def test(self, value):
        print value

#     def set_node(self, node):
#         index_path = node.index_path()
#         index = self.model.get_index_from_row_path(index_path, 0)
#
#         self.set_current_index(index)

    def get_fbx_object(self):
        return self.session_model.get_fbx_object(
            self._current_index
        )

    def text_changed(self):
        #         return
        # TODO pass to BpItemToListProxyModel as filter
        # and display unfiltered results
        value = self.text()
        self._filter_model.setFilterWildcard(value)


class PropertyFnStrDeligate(Qt.QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(PropertyFnStrDeligate, self).__init__(parent=parent)

    def get_prop_fn(self, index):

        property_model = index.model()
        #         prop_fn = property_model.get_property_fn(index)
        prop_item = property_model.get_property_item(index)

        prop_fn = prop_item.property_object()

        return prop_fn

    def createEditor(self, parent, option, index):
        """
        In addition, we connect the combobox's activated() signal to the emitCommitData() slot
        to emit the QAbstractItemDelegate::commitData() signal whenever the user chooses an item
        using the combobox.

        This ensures that the rest of the application notices the change and updates itself.
        """

        property_model = index.model()
        prop_item = property_model.get_property_item(index)

        prop_fn = self.get_prop_fn(index)

        row = index.row()
        column = index.column()

        if column == 1:
            # TODO stuff
            if isinstance(prop_fn, bfProperty.FSEnumProperty):

                editor = Qt.QtWidgets.QComboBox(parent)

#                 editor.activated.connect(
#                     self.emitCommitData
#                 )

                editor.addItems(prop_fn.ENUM_NAMES)

            elif isinstance(prop_fn, bfProperty.InputReferenceProperty):

                fbx_object = prop_fn.Get()

                editor = BrInputReferenceDeligateEditor(parent)

                editor.setSessionModel(
                    property_model.session_model()
                )

                editor.set_current_fbx_object(fbx_object)

                editor.complete_signal.connect(
                    self.emitCommitAndClose
                )

            else:
                print "defaulting to editor"
                editor = Qt.QtWidgets.QLineEdit(parent)

#                 editor.editingFinished.connect(
#                     self.emitCommitData
#                 )

        else:
            editor = Qt.QtWidgets.QLineEdit(parent)
#
#             editor.editingFinished.connect(
#                 self.emitCommitData
#             )

        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.QtCore.Qt.EditRole)

        prop_fn = self.get_prop_fn(index)

        if prop_fn is None:
            return

        row = index.row()
        column = index.column()

        if column == 1:
            # TODO stuff
            pass

        if isinstance(prop_fn, bfProperty.FSEnumProperty):
            editor.setCurrentIndex(prop_fn.GetIndex())

        elif isinstance(
            prop_fn,
            (
                bfProperty.InputReferenceProperty,
                bfProperty.InputReferenceArrayProperty
            )
        ):
            # custom editor inherits from QLineEdit
            # so we can set as normal
            editor.setText(value)

        else:
            editor.setText(value)

    def setModelData(self, editor, model, index):

        prop_fn = self.get_prop_fn(index)

        if prop_fn is None:
            return

        if isinstance(prop_fn, bfProperty.FSEnumProperty):
            value = editor.currentText()

        else:
            value = editor.text()

            print type(value)

        row = index.row()
        column = index.column()

        if column == 1:
            # TODO stuff
            pass

        try:

            #             bp_str = bfData.get_bpstr_data_type(
            #                 prop_fn.Property()
            #             )
            #
            #             value = bp_str.from_str(value)
            #
            #             print value

            model.setData(index, value, Qt.QtCore.Qt.EditRole)

        except (bfCore.BFbxError, bpStr.BpStrException) as err:

            """
            NOTE

            We induced some errors/strange behaviour with this

            Because we connected the editor to emitCommitData()
            that meant this was being called twice each time.

            In cases where we wanted to show a Dialog with an error
            message, qt was trying to display two at the same time,
            presumably in seperate threads, causing the application to crash.

            Removing this redundant connection resolves the error.

            But as a safer solution, calling setModal() and show()
            seems to be thread safe, and worse case we just get two
            dialogs, but no crash.

            """

            if False:
                # "standard" but longer method
                # not thread safe
                Qt.QtWidgets.QMessageBox.warning(
                    editor.parent(),
                    err.__class__.__name__,
                    err.message,
                    Qt.QtWidgets.QMessageBox.Ok
                )
            else:
                # custom method
                err_dialog = bpQtWidgets.BpExceptionMessageBox(
                    err, parent=editor.parent()
                )

                if True:
                    # thread safe method
                    err_dialog.setModal(True)  # or setWindowModality()
                    err_dialog.show()
                else:
                    # apparantly not thread safe?
                    err_dialog.exec_()

                return False

#

#     def updateEditorGeometry(self, editor, option, index):
#         editor.setGeometry(option.rect)

    def emitCommitAndClose(self):
        self.emitCommitData()
        self.emitCloseEditor()

    def emitCommitData(self):
        """
        The emitCommitData() slot simply emit the QAbstractItemDelegate::commitData() signal
        for the editor that triggered the slot.

        This signal must be emitted when the editor widget has completed editing the data,
        and wants to write it back into the model.
        """
        print "emitting stuff"

        self.commitData.emit(
            self.sender()
        )

    def emitCloseEditor(self):
        self.closeEditor.emit(
            self.sender(),
            self.NoHint
        )
