'''

Created on 9 Jun 2018

https://www.youtube.com/watch?v=fxLIGaTZ4pk

table model

'''


from PySide import QtGui, QtCore
import sys


class PaletteTableModel(QtCore.QAbstractTableModel):

    def __init__(self, colors=[[]], headers=[], parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._colors = colors
        self._headers = headers

    def headerData(self, section, orientation, role):
        """ called by view when naming rows and columns
        """
        if role == QtCore.Qt.DisplayRole:

            if orientation == QtCore.Qt.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
                else:
                    return "Palette {}".format(section)
            else:
                return "Color {}".format(section)

    def rowCount(self, parent):
        """ called by view to know how many rows to create
        """
        return len(self._colors)

    def columnCount(self, parent):
        return len(self._colors[0])

    def data(self, index, role):
        """
            called by view when populating item field

            http://doc.qt.io/qt-5/qt.html#ItemDataRole-enum

        """

        row = index.row()
        column = index.column()
        color = self._colors[row][column]

        if role == QtCore.Qt.FontRole:
            # not called by comboBox?
            return QtGui.QFont("Ariel", 20)

        if role == QtCore.Qt.TextAlignmentRole:
            # not called by comboBox?
            return QtCore.Qt.AlignmentFlag.AlignCenter

        if role == QtCore.Qt.BackgroundRole:
            return color

        if role == QtCore.Qt.EditRole:
            # called when user tries to edit
            return "editing: " + color.name()

        if role == QtCore.Qt.ToolTipRole:
            return "Hex code: " + color.name()

        if role == QtCore.Qt.DecorationRole:

            pixmap = QtGui.QPixmap(26, 26)
            pixmap.fill(color)

            icon = QtGui.QIcon(pixmap)

            return icon

        if role == QtCore.Qt.DisplayRole:

            return color.name()

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

        row = index.row()
        column = index.column()

        if role == QtCore.Qt.EditRole:

            color = QtGui.QColor(value)

            if color.isValid():  # has the user typed the hex code correctly?
                self._colors[row][column] = color

                # send a signal to other views that they need to update
                # emit(top-left index, bottom-right index) to update many items
                # at once
                self.dataChanged.emit(index, index)

                return True  # the item display value is updated next time self.data() is called
            else:
                return False  # item stays as-is

        return False

    def insertRows(self, position, row_count, parent=QtCore.QModelIndex()):
        """ parent is ignored, will be used for tree view later
        """

        # send signal to views that were are about to modify the following ros
        # (parent, first row, last row)
        self.beginInsertRows(parent, position, position + row_count - 1)

        for _ in range(row_count):
            # insert default values into our list
            default_values = [QtGui.QColor("#000000")] * self.columnCount(None)
            self._colors.insert(position, default_values)

        # send a signal to views that we are done editing and to update items
        self.endInsertRows()

    def insertColumns(self,  position, column_count, parent=QtCore.QModelIndex()):

        self.beginInsertColumns(parent, position, position + column_count - 1)

        """
        #tutorial method
        for _ in range(column_count):
            for i in range(self.rowCount(None)):
                self._colors[i].insert(position, QtGui.QColor("#000000"))
        """

        for _ in range(column_count):
            for row in self._colors:
                row.insert(position, QtGui.QColor("#000000"))

        self.endInsertColumns()

    def removeRows(self, position, row_count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + row_count - 1)

        for _ in range(row_count):
            self._colors.pop(position)

        self.endRemoveRows()

    def removeColumns(self, position, column_count, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, position, position + column_count - 1)

        for row in self._colors:
            for _ in range(column_count):
                row.pop(position)

        self.endRemoveColumns()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")

    # ALL OF OUR VIEWS
    listView = QtGui.QListView()
    listView.show()

    # tree view crashes with table model!
    #treeView = QtGui.QTreeView()
    # treeView.show()

    comboBox = QtGui.QComboBox()
    comboBox.show()

    tableView = QtGui.QTableView()
    tableView.show()

    red = QtGui.QColor(255, 0, 0)
    green = QtGui.QColor(0, 255, 0)
    blue = QtGui.QColor(0, 0, 255)

    model = PaletteTableModel([
        [red, green, blue],
        [green, blue, red],
        [blue, red, green],
    ], headers=["poop", "thing"])

    model.insertColumns(1, 2)
    model.insertRows(1, 5)
    #model.removeRows(1, 2)
    #model.removeColumns(1, 2)

    listView.setModel(model)
    comboBox.setModel(model)
    tableView.setModel(model)
    # treeView.setModel(model)

    sys.exit(app.exec_())
