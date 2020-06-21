'''
Created on 6 Jun 2018

@author: Bren
'''


"""
https://www.tutorialspoint.com/pyqt/pyqt_drag_and_drop.htm


https://stackoverflow.com/questions/37795528/why-do-i-not-see-the-drop-indicator-in-a-qtableview


"""

import sys
# from PySide import QtGui, QtCore

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

from brenpy.qt.item import bpQtItemsWidgets

class Item(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.children = []
        self.parent = None

    def index(self):
        if self.parent is None:
            return 0
        else:
            return self.parent.children.index(self)

    def set_child_index(self, index, child_item):
        self.children.remove(child_item)
        self.children.insert(index, child_item)

class NullItem(object):
    def __init__(self):
        self.parent = None

class DragModel(QtCore.QAbstractItemModel):
    def __init__(self):
        super(DragModel, self).__init__()
        self.root_item = Item("Root", 0)
        self.id_data = {}
        self.null_item = NullItem()

        item_id = 1

        for i in range(6):
            item = Item("item{}".format(i), item_id)
            item.parent = self.root_item
            self.root_item.children.append(item)
            self.id_data[item_id] = item

            item_id += 1

            for j in range(3):
                child = Item("item{}_{}".format(i, j), item_id)
                child.parent = item
                item.children.append(child)
                self.id_data[item_id] = child

                item_id += 1

    def index(self, row, column, parent):
        if parent.isValid():
            parent_item = parent.internalPointer()
            # parent_item = self._items[parent.row()]

            if row >= len(parent_item.children):
                # raise Exception("poop")
                item = self.null_item
            else:
                item = parent_item.children[row]

        else:
            item = self.root_item

        return self.createIndex(row, column, item)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        item = index.internalPointer()

        if item.parent is None:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(item.parent.index(), 0, item.parent)

    def rowCount(self, index):
        if not index.isValid():
            return 1 # root item

        item = index.internalPointer()

        # if item.parent is not None:
        #     return 0

        return len(item.children)

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            if index.column() == 0:
                return index.internalPointer().name
            elif index.column() == 1:
                return index.internalPointer().id

        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        return True

    def supportedDragActions(self):
        # return QtCore.Qt.DropAction | QtCore.Qt.CopyAction | QtCore.Qt.MoveAction #| QtCore.Qt.InternalMoveAction
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction  # | QtCore.Qt.InternalMoveAction
        # return QtCore.Qt.MoveAction  # | QtCore.Qt.InternalMoveAction

    def supportedDropActions(self):
        # return QtCore.Qt.DropAction | QtCore.Qt.CopyAction | QtCore.Qt.MoveAction #| QtCore.Qt.InternalMoveAction
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction  # | QtCore.Qt.InternalMoveAction
        # return QtCore.Qt.MoveAction  # | QtCore.Qt.InternalMoveAction

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        flags = QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled

        return flags

    def mimeTypes(self):
        return ['id_csv_data']

    def mimeData(self, indexes):

        mimedata = QtCore.QMimeData()
        text_list = [str(i.internalPointer().id) for i in indexes]
        csv_data = ",".join(text_list)

        # IMPORTANT
        # for some reason if we don't setData
        # and only setText
        # the dropIndicator doesn't show!
        # in fact painting seems to be blocked entirely
        # TODO maybe the mime data is erroring and failing to show an error?
        mimedata.setData("id_csv_data", csv_data)

        # mimedata.setText("test")

        return mimedata

    def dropMimeData(self, mime_data, action, row, column, parent):
        csv_data = mime_data.data('id_csv_data')
        item_ids = []

        for i in csv_data.split(","):
            item_id = int(i)
            if item_id not in item_ids:
                item_ids.append(item_id)

        items = [self.id_data[i] for i in item_ids]

        parent_item = parent.internalPointer()

        print "parent {}, row {}, column {}, action {}, item ids {}".format(
            parent_item.id, row, column, action, item_ids
        )

        # if row == -1:
        #     child_index = 0
        # else:
        #     child_index = row

        self.insert_items(items, parent_item, row)

        return True

    def canDropMimeData(self,  mime_data, action, row, column, parent):

        return True

    def insert_items(self, items, parent_item, index):
        self.beginResetModel()

        # make sure all items are children of parent item
        for item in items:
            if item.parent is not parent_item:
                item.parent.children.remove(item)
                item.parent = parent_item
                parent_item.children.append(item)

        # set indices
        # if index is -1 then we don't need to change index
        if index != -1:
            for item in items:
                parent_item.set_child_index(index, item)
                index += 1

        self.endResetModel()

        return True

    # note the provided methods aren't that flexible for what we want
    # it only supports moving sequential rows from a single parent

    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
        pass

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        """
        moveRows(const QModelIndex &sourceParent, int sourceRow, int count, const QModelIndex &destinationParent, int destinationChild)
        """
        pass
        # we can't use bgeinMoveRows in maya? TODO test this

        # # TODO is this better?
        # self.layoutAboutToBeChanged.emit()
        #
        # # do stuff
        #
        # self.layoutChanged.emit()

    def insertRow(self, row, parentIndex=QtCore.QModelIndex):
        pass
        # self.beginInsertRows(parentIndex, row, row)
        #
        # # TODO do stuff
        #
        # self.endInsertRows()
        #
        # return True

    def insertRows(self, row, count, parentIndex=QtCore.QModelIndex):
        pass

    def removeRow(self, row, parentIndex=QtCore.QModelIndex):
        pass

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex):
        pass

    def insertColumn(self, *args, **kwargs):
        pass

    def insertColumns(self, *args, **kwargs):
        pass

    def hasChildren(self, index):
        if not index.isValid():
            return True

        item = index.internalPointer()
        return len(item.children) > 0


class DragListExample1(object):
    def __init__(self):
        super(DragListExample1, self).__init__()

        self._model = DragModel()

        self._view = QtWidgets.QTreeView()
        self._view.setModel(self._model)

        self._view.setSelectionMode(
            # QtWidgets.QAbstractItemView.SingleSelection
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        self._view.setDragEnabled(True)
        self._view.setAcceptDrops(True)
        self._view.setDropIndicatorShown(True)
        # self._view.setDragDropMode(self._view.InternalMove)
        self._view.setDragDropMode(self._view.DragDrop)

        self._model.modelReset.connect(self._view.expandAll)

        self._view.expandAll()
        self._view.setColumnWidth(0, 200)
        self._view.setGeometry(
            100,
            100,
            300,
            600
        )

        self._view.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    test = DragListExample1()

    app.exec_()
