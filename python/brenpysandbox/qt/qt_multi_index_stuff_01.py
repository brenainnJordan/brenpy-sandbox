'''
Created on 14 Aug 2019

@author: Bren
'''

import sys

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

TEST_DATA = [
    ("a", "aa", [1, 2, 3]),
    ("b", "bb", [4, 5, 6]),
    ("c", "cc", [7, 8, 9, 10, 11]),
]


class Data(object):
    def __init__(self, init_value=0):
        super(Data, self).__init__()
        self.isSubChild = False
        self.hasSubChildren = False

        self._value = init_value

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value

#
# class SubChildIndex(object):
#     def __init__(self, init_value=0):
#         super(SubChildIndex, self).__init__()
#         self._value = init_value
#
#     def value(self):
#         return self._value
#
#     def set_value(self, value):
#         self._value = value
#
#
# class HasSubChildren():
#     pass
#
#
# class HasNoSubChildren():
#     pass
#
#
# class IsSubChild():
#     pass
#
#
# class IsNotSubChild():
#     pass


class TestModel(Qt.QtCore.QAbstractItemModel):

    def __init__(self, parent=None):
        super(TestModel, self).__init__(parent)

        self.cache_data = []
        self.sub_child_cache = []

        for row_id, row in enumerate(TEST_DATA):
            row_cache = []

            for column_id, column in enumerate(row):
                data = Data([row_id, column_id])

                if column_id == 2:
                    data.hasSubChildren = True

                    for sub_child_id, sub_child in enumerate(column):
                        sub_child_data = Data()
                        sub_child_data.isSubChild = True

                        sub_child_data.set_value(
                            [row_id, column_id, sub_child_id]
                        )

                        self.sub_child_cache.append(sub_child_data)
                row_cache.append(data)

            self.cache_data.append(row_cache)

    def parent(self, index):
        """Create an index for parent object of requested index.
        # TODO somethings broke!
        """

        if not index.isValid():
            return Qt.QtCore.QModelIndex()

#         row = index.row()
#         column = index.column()

        obj = index.internalPointer()
        data_path = obj.value()

        if obj.isSubChild:
            parent_obj = self.cache_data[data_path[0]][data_path[1]]

            return self.createIndex(
                data_path[0], data_path[1], parent_obj
            )

        else:
            return Qt.QtCore.QModelIndex()

    def index(self, row, column, parent_index):
        """

        """

        if parent_index.isValid() and column == 2:
            #                 parent_row = parent_index.row()
            #                 parent_column = parent_index.column()
            #
            #                 data_path = [parent_row, parent_column, row]
            #                 data = Data(data_path)
            #                 data.isSubChild = True
            obj = self.sub_child_cache[row]
            return self.createIndex(row, column, obj)
#
#             else:
#                 data_path = [row, column]
#                 data = Data(data_path)
#                 data.hasSubChildren = True
#
#                 return self.createIndex(row, column, data)

        obj = self.cache_data[row][column]
        return self.createIndex(row, column, obj)

    def rowCount(self, index):
        if not index.isValid() or True:
            # if index is not valid, then we must be at root level
            print len(TEST_DATA)
            return len(TEST_DATA)

        else:
            obj = index.internalPointer()

            if obj.hasSubChildren:

                row = index.row()
                column = index.column()

                sub_children = TEST_DATA[row][column]

                return len(sub_children)

            else:
                return 0

    def columnCount(self, index=None):
        return 3

    def data(self, index, role):
        """

        """

        if not index.isValid():
            return

        row = index.row()
        column = index.column()
        obj = index.internalPointer()

#         parent_obj = parent_index.internalPointer()

        if obj.isSubChild:
            parent_index = index.parent()
            parent_row = parent_index.row()
            parent_column = parent_index.column()

            return TEST_DATA[parent_row][parent_column][row]

        else:
            print TEST_DATA[row][column]
            return TEST_DATA[row][column]

    def setData(self, index, value, role=Qt.QtCore.Qt.EditRole):
        """
        """
        return False

        if not index.isValid():
            return False

        row = index.row()
        column = index.column()

        return False

    def flags(self, index):
        """ hard-coded item flags """

        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable | Qt.QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):

        headers = ["blah", "poop", "things"]

        if role == Qt.QtCore.Qt.DisplayRole:
            if orientation == Qt.QtCore.Qt.Horizontal:
                if section > len(headers):
                    return "null"
                else:
                    return headers[section]

        return None

    def insertColumn(self, *args, **kwargs):
        raise NotImplementedError("Use addNode or createNode instead")

    def insertColumns(self, *args, **kwargs):
        raise NotImplementedError("Use addNodes or createNodes instead")

    def insertRow(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNode instead")

    def insertRows(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNodes instead")


class Test1(object):
    def __init__(self):

        self.model = TestModel()

        self.tree = Qt.QtWidgets.QTreeView()
        self.table = Qt.QtWidgets.QTableView()
        self.tree.setModel(self.model)
        self.table.setModel(self.model)

        self.tree.show()
        self.table.show()


if __name__ == "__main__":
    #     test = BrIdData(init_value=3.0)
    #     print test.value()

    app = Qt.QtWidgets.QApplication(sys.argv)

    test = Test1()

    sys.exit(app.exec_())
