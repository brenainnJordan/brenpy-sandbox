'''Simple spin box deligate example

Created on 1 Aug 2019

@author: Bren

Docs:
https://doc.qt.io/qt-5/model-view-programming.html#delegate-classes

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


class SpinBoxDeligate(Qt.QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        """
        We subclass the delegate from QStyledItemDelegate
        because we do not want to write custom display functions.

        However, we must still provide functions to manage the editor widget.

        Note that no editor widgets are set up when the delegate is constructed.
        We only construct an editor widget when it is needed.

        """
        Qt.QtWidgets.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        In this example, when the table view needs to provide an editor,
        it asks the delegate to provide an editor widget that is appropriate for the item being modified.

        The createEditor() function is supplied with everything that the delegate needs
        to be able to set up a suitable widget.

        Note that we do not need to keep a pointer to the editor widget
        because the view takes responsibility for destroying it when it is no longer needed.
        """

        # our editor will be a QSpinBox widget
        editor = Qt.QtWidgets.QSpinBox(parent)

        # something?
        editor.setFrame(False)

        # set some specific behaviour for spin box
        editor.setMinimum(0.0)
        editor.setMaximum(100.0)

        # return widget
        return editor

    def setEditorData(self, editor, index):
        """
        The delegate must provide a function to copy model data into the editor.
        In this example, we read the data stored in the display role,
        and set the value in the spin box accordingly.

        In this example, we know that the editor widget is a spin box,
        but we could have provided different editors for different types of data in the model,
        in which case we would need to cast the widget to the appropriate type
        before accessing its member functions.

        """
        value = index.model().data(index, Qt.QtCore.Qt.EditRole)  # .toInt()
        # static cast?
        if not isinstance(value, (int, float)):
            return
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        """
        When the user has finished editing the value in the spin box,
        the view asks the delegate to store the edited value in the model
        by calling the setModelData() function.

        Since the view manages the editor widgets for the delegate,
        we only need to update the model with the contents of the editor supplied.

        In this case, we ensure that the spin box is up-to-date,
        and update the model with the value it contains using the index specified.

        The standard QStyledItemDelegate class informs the view when it has finished editing
        by emitting the closeEditor() signal.

        The view ensures that the editor widget is closed and destroyed.

        In this example, we only provide simple editing facilities,
        so we need never emit this signal.

        """

        # static cast?
        #         edit.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """
        It is the responsibility of the delegate to manage the editor's geometry.

        The geometry must be set when the editor is created,
        and when the item's size or position in the view is changed.

        Fortunately, the view provides all the necessary geometry information inside a view option object.

        In this case, we just use the geometry information provided by the view option in the item rectangle.

        A delegate that renders items with several elements would not use the item rectangle directly.

        It would position the editor in relation to the other elements in the item.
        """

        editor.setGeometry(option.rect)


class Data(object):
    def __init__(self, init_value=0.0):
        self._value = init_value

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class SimpleListModel(Qt.QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        Qt.QtCore.QAbstractListModel.__init__(self, parent)

        self._data = [Data(init_value=i) for i in range(10)]
        print self._data

    def rowCount(self, index):
        if not index.isValid():
            pass

        return len(self._data)

    def index(self, row, column, parent_index):
        if column > 0:
            return

        if row > len(self._data):
            return

        if parent_index.isValid():
            pass

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


class View():
    # TODO
    def EditTriggers(self):
        pass


if __name__ == "__main__":
    app = Qt.QtWidgets.QApplication(sys.argv)

    # ALL OF OUR VIEWS
    listView = Qt.QtWidgets.QListView()
    listView.show()
#
#     treeView = QtGui.QTreeView()
#     treeView.show()
#
#     comboBox = QtGui.QComboBox()
#     comboBox.show()
#
#     tableView = QtGui.QTableView()
#     tableView.show()

    model = SimpleListModel()

    listView.setModel(model)

    """
    Warning: You should not share the same instance of a delegate between views.
    Doing so can cause incorrect or unintuitive editing behavior since each view connected
    to a given delegate may receive the closeEditor() signal, and attempt to access,
    modify or close an editor that has already been closed.
    """

    deligate = SpinBoxDeligate()

    listView.setItemDelegate(
        deligate
    )

#     comboBox.setModel(model)
#     tableView.setModel(model)
#     treeView.setModel(model)

    sys.exit(app.exec_())
