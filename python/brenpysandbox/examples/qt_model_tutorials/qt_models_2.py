'''
Created on 9 Jun 2018

https://www.youtube.com/watch?v=azGfJ7-wK_g


Sharing an editable model across views


'''


from PySide import QtGui, QtCore
import sys


class PaletteListModel(QtCore.QAbstractListModel):

    def __init__(self, colors=[], parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self._colors = colors

    def headerData(self, section, orientation, role):
        """ called by view when naming rows and columns
        """
        if role == QtCore.Qt.DisplayRole:

            if orientation == QtCore.Qt.Horizontal:
                return "Palette"
            else:
                return "Color {}".format(section)

    def rowCount(self, parent):
        """ called by view to know how many rows to create
        """
        return len(self._colors)

    def data(self, index, role):
        """
            called by view when populating item field

            http://doc.qt.io/qt-5/qt.html#ItemDataRole-enum

        """

        if role == QtCore.Qt.FontRole:
            # not called by comboBox?
            return QtGui.QFont("Ariel", 20)

        if role == QtCore.Qt.TextAlignmentRole:
            # not called by comboBox?
            return QtCore.Qt.AlignmentFlag.AlignCenter

        if role == QtCore.Qt.BackgroundRole:
            return self._colors[index.row()]

        if role == QtCore.Qt.EditRole:
            # called when user tries to edit
            return "editing: " + self._colors[index.row()].name()

        if role == QtCore.Qt.ToolTipRole:
            return "Hex code: " + self._colors[index.row()].name()

        if role == QtCore.Qt.DecorationRole:

            row = index.row()
            value = self._colors[row]

            pixmap = QtGui.QPixmap(26, 26)
            pixmap.fill(value)

            icon = QtGui.QIcon(pixmap)

            return icon

        if role == QtCore.Qt.DisplayRole:

            row = index.row()
            value = self._colors[row]

            return value.name()

    def flags(self, index):
        """ hard-coded item flags
            index is ignored
            this would probably be settable as normal if *args and **kwargs were passed into __init__
        """
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """ called when user tries to edit an item
            must return true if successful and false if not
            if returned false, item stays as is!
        """

        if role == QtCore.Qt.EditRole:
            row = index.row()
            color = QtGui.QColor(value)

            if color.isValid():  # has the user typed the hex code correctly?
                self._colors[row] = color

                # send a signal to other views that they need to update
                # emit(top-left index, bottom-right index) to update many items
                # at once
                self.dataChanged.emit(index, index)

                return True  # the item display value is updated next time self.data() is called
            else:
                return False  # item stays as-is

        return False


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")

    # ALL OF OUR VIEWS
    listView = QtGui.QListView()
    listView.show()

    treeView = QtGui.QTreeView()
    treeView.show()

    comboBox = QtGui.QComboBox()
    comboBox.show()

    tableView = QtGui.QTableView()
    tableView.show()

    red = QtGui.QColor(255, 0, 0)
    green = QtGui.QColor(0, 255, 0)
    blue = QtGui.QColor(0, 0, 255)

    model = PaletteListModel([red, green, blue])

    listView.setModel(model)
    comboBox.setModel(model)
    tableView.setModel(model)
    treeView.setModel(model)

    sys.exit(app.exec_())
