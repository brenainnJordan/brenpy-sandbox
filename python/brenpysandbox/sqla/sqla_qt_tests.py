'''
Created on 18 Sep 2018

@author: Bren
'''
'''
Created on 17 Sep 2018

@author: Bren
'''

import os
import sys

import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import scandir

from PySide import QtGui, QtCore


class DirEntryModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(DirEntryModel, self).__init__(parent)
        self._query_data = []

        self._horizontal_headers = [
            "name", "path", "size"
        ]

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < len(self._horizontal_headers):
                    return self._horizontal_headers[section]
                else:
                    return "other"

    def rowCount(self):
        """ called by view to know how many rows to create
        """
        return len(self._query_data)

    def columnCount(self, index=None):
        return len(self._horizontal_headers)

    def index(self, row, column, *args, **kwargs):
        """
            ** Overide Method **

            Create QModelIndex representing desired model item.

            The term "index" in this case is not used as the index of a list such as an integer
            "index" refers to a QModelIndex class instance, which contains a pointer to our data.
            The data in this case is a Node class instance.

            http://doc.qt.io/qt-5/qabstractitemmodel.html#createIndex

            I guess a QModelIndex is a more portable/abstract represenation of this model instance

            :TODO find out when this is called?
        """

        data = self._query_data[row]

        if not data:  # i mean why not?
            return QtCore.QModelIndex()  # return empty index

        # create new index with pointer to desired Node
        index = self.createIndex(row, column, data)
        return index

    def data(self, index, role):
        """
            called by view when populating item field

            http://doc.qt.io/qt-5/qt.html#ItemDataRole-enum

        """

        if role == QtCore.Qt.DisplayRole:
            data = index.internalPointer()

            row = index.row()
            value = getattr(data, self._horizontal_headers[row])
            return value

    def flags(self, *args, **kwargs):
        """ hard-coded item flags
            index is ignored
            this would probably be settable as normal if *args and **kwargs were passed into __init__
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, *args, **kwargs):
        """ called when user tries to edit an item
            must return true if successful and false if not
            if returned false, item stays as is!
        """
        return False


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    gui = QtGui.QTableView()
    model = DirEntryModel()
    gui.setModel(model)
    gui.show()

    sys.exit(app._exec())
