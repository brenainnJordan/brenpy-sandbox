'''Combo box deligate example

Created on 1 Aug 2019

@author: Bren

Docs:

https://doc.qt.io/qt-5/qtwidgets-widgets-icons-example.html#imagedelegate-class-definition

Note:

The above example uses persistent editors by calling the following:
    QTableWidget *imagesTable;
    QTableWidgetItem *stateItem = new QTableWidgetItem(...)
    imagesTable->setItem(row, 2, stateItem);
    imagesTable->openPersistentEditor(modeItem);

Instead of using model/view objects.

There doesn't appear to be a clean way to use persistent editors with view objects.
See hacky method at the bottom of this file.

'''

import sys
import os
import random

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

OPTIONS = [
    "poop",
    "things",
    "test",
    "anus"
]


class ComboBoxDeligate(Qt.QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        Qt.QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        Our reimplementation creates and populates a combobox instead of the default line edit.

        The contents of the combobox depends on the column in the table for which the editor is requested.

        Column 1 contains the QIcon modes, whereas column 2 contains the QIcon states. (skipped for now)

        In addition, we connect the combobox's activated() signal to the emitCommitData() slot
        to emit the QAbstractItemDelegate::commitData() signal whenever the user chooses an item
        using the combobox.

        This ensures that the rest of the application notices the change and updates itself.
        """

        editor = Qt.QtWidgets.QComboBox(parent)

        editor.addItems(OPTIONS)

        editor.activated.connect(
            self.emitCommitData
        )

        return editor

    def setEditorData(self, editor, index):
        combo_index = editor.findText(
            index.model().data(
                index, Qt.QtCore.Qt.EditRole
            ),  # .toString(),
            Qt.QtCore.Qt.MatchExactly
        )

        editor.setCurrentIndex(combo_index)

    def setModelData(self, editor, model, index):
        # TODO use index instead
        value = editor.currentText()

        model.setData(index, value, Qt.QtCore.Qt.EditRole)


#     def updateEditorGeometry(self, editor, option, index):
#         editor.setGeometry(option.rect)

    def emitCommitData(self):
        """
        The emitCommitData() slot simply emit the QAbstractItemDelegate::commitData() signal
        for the editor that triggered the slot.

        This signal must be emitted when the editor widget has completed editing the data,
        and wants to write it back into the model.
        """
        self.commitData.emit(self.sender())


class Data(object):
    def __init__(self, init_value=""):
        self._value = init_value

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class SimpleListModel(Qt.QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        Qt.QtCore.QAbstractListModel.__init__(self, parent)

        self._data = [
            Data(OPTIONS[
                random.randint(0, len(OPTIONS) - 1)
            ])
            for _ in range(10)
        ]

    def rowCount(self, index):
        #         if not index.isValid():
        #             pass

        return len(self._data)

    def index(self, row, column, parent_index):
        if column > 0:
            return

        if row > len(self._data):
            return

#         if parent_index.isValid():
#             pass

        data = self._data[row]

        index = self.createIndex(row, column, data)

        return index

    def data(self, index, role):

        if not index.isValid():
            return

        row = index.row()
        column = index.column()
        data = index.internalPointer()

        if role in [Qt.QtCore.Qt.EditRole]:
            value = data.value()
            return value

        elif role in [Qt.QtCore.Qt.DisplayRole]:
            return data.value()

    def setData(self, index, value, role):

        if not index.isValid():
            return False

        row = index.row()
        column = index.column()
        data = index.internalPointer()

        if role == Qt.QtCore.Qt.EditRole:
            data.set_value(value)

        # Qt expects us to return True if successful
        return True

    def flags(self, index):
        return Qt.QtCore.Qt.ItemIsEditable | Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable


class View(Qt.QtWidgets.QListView):
    """Custom list view.

    Failed attempt to use:
    openPersistentEditor(const QModelIndex &index)

    https://stackoverflow.com/questions/528366/how-do-i-tell-qt-to-always-show-an-editor-in-a-qtableview

    """

    def __init__(self, parent=None):
        Qt.QtWidgets.QListView.__init__(self, parent)

    def rowsInserted(self, parent, start_row, end_row):
        # Not called when syncing with model
        # no way to do this with a view?
        for i in range(start_row, end_row + 1):
            index = self.model().index(i, 0, parent)
            self.openPersistentEditor(index)


class Test1():
    def __init__(self):
        # ALL OF OUR VIEWS
        self.listView = View()
        self.listView.show()

        self.listView2 = Qt.QtWidgets.QListView()
        self.listView2.show()
    #
    #     treeView = QtGui.QTreeView()
    #     treeView.show()
    #
    #     comboBox = QtGui.QComboBox()
    #     comboBox.show()
    #
    #     tableView = QtGui.QTableView()
    #     tableView.show()

        self.model = SimpleListModel()

        self.listView.setModel(self.model)
        self.listView2.setModel(self.model)

        """
        Warning: You should not share the same instance of a delegate between views.
        Doing so can cause incorrect or unintuitive editing behavior since each view connected
        to a given delegate may receive the closeEditor() signal, and attempt to access,
        modify or close an editor that has already been closed.
        """

        if True:
            self.deligate = ComboBoxDeligate()

            self.listView.setItemDelegate(
                self.deligate
            )
            # also
    #         setItemDelegateForColumn(int column, QAbstractItemDelegate *delegate)
    #         setItemDelegateForRow(int row, QAbstractItemDelegate *delegate)

        if False:
            # only way to display persistent editors...
            # seems to have some sync issues when sharing data
            # with other views
            for i in range(self.model.rowCount(None)):
                index = self.model.index(i, 0, None)
                self.listView.openPersistentEditor(index)

        if True:
            self.deligate2 = ComboBoxDeligate()

            self.listView2.setItemDelegate(
                self.deligate2
            )

    #     comboBox.setModel(model)
    #     tableView.setModel(model)
    #     treeView.setModel(model)


if __name__ == "__main__":
    app = Qt.QtWidgets.QApplication(sys.argv)

    test = Test1()

    sys.exit(app.exec_())
