"""
Stuff
"""

import sys

import fbx

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

from brenfbx.core import bfData
reload(bfData)

from brenfbx.qt import bfIcons


class BFbxTypeModel(Qt.QtCore.QAbstractListModel):
    """List model of all available FbxObject classes with appropriate icons.
    TODO use class id objects instead?
    """

    kFbxClassRole = Qt.QtCore.Qt.UserRole

    def __init__(self, parent=None):
        super(BFbxTypeModel, self).__init__(parent=parent)

        self.types = bfData.get_fbx_object_types()

    def rowCount(self, index):
        return len(self.types)

    def data(self, index, role):
        """
        """

        if not index.isValid():
            return

        row = index.row()
        fbx_cls = self.types[row]

        if role in [Qt.QtCore.Qt.DisplayRole]:
            return fbx_cls.__name__

        elif role in [Qt.QtCore.Qt.DecorationRole]:
            return bfIcons.get_fbx_object_icon(fbx_cls)

        elif role in [self.kFbxClassRole]:
            return fbx_cls


class BFbxClassIdBoolListModel(Qt.QtCore.QAbstractListModel):
    """List model of all available FbxObject classes with appropriate icons.
    """

    kFbxClassRole = Qt.QtCore.Qt.UserRole

    def __init__(self, parent=None, fbx_manager=None):
        super(BFbxClassIdBoolListModel, self).__init__(parent=parent)

        # fbx manager must be instanced to manage FbxClassId objects
        if fbx_manager is None:
            self.fbx_manager = fbx.FbxManager.Create()
        else:
            self.fbx_manager = fbx_manager

        self._data_root = bfData.FbxClassIdBoolRoot(self.fbx_manager)
#         self.data.debug()

    def data_root(self):
        return self._data_root

    def set_data_root(self, data_root):
        """
        TODO checks
        """
        self.beginResetModel()
        self._data_root = data_root
        self.endResetModel()

    def rowCount(self, index):
        return self._data_root.item_count()

    def flags(self, index):
        """ hard-coded item flags """
        return Qt.QtCore.Qt.ItemIsUserCheckable | Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        """

        if not index.isValid():
            return

        row = index.row()
        item = self._data_root.get_item(row)

        return self.get_item_data(item, role)

    @staticmethod
    def get_item_data(item, role):
        """TODO maybe move this out of class?
        Cleanup a bit
        """
        if role in [Qt.QtCore.Qt.CheckStateRole]:
            if item.value():
                return Qt.QtCore.Qt.Checked
            else:
                return Qt.QtCore.Qt.Unchecked

        elif role in [Qt.QtCore.Qt.DisplayRole]:
            return item.class_id().GetName()

        elif role in [Qt.QtCore.Qt.DecorationRole]:
            return bfIcons.get_fbx_object_icon(item.class_id())

        elif role in [BFbxClassIdBoolListModel.kFbxClassRole]:
            return item.class_id()
        else:
            return None

    def setData(self, index, value, role):

        if not index.isValid():
            return

        item = self._data_root.get_item(index.row())
        return self.set_item_data(item, value, role)

    @staticmethod
    def set_item_data(item, value, role):
        """TODO maybe move this out of class?
        """
        if role in [Qt.QtCore.Qt.CheckStateRole]:

            if value == Qt.QtCore.Qt.Checked:
                item.set_value(True)
                return True

            elif value == Qt.QtCore.Qt.Unchecked:
                item.set_value(False)
                return True

            else:
                return False

        return False

    def debug(self):

        self._data_root.debug()


class BFbxClassIdBoolTreeModel(Qt.QtCore.QAbstractItemModel):
    """Tree model of all available FbxObject classes with appropriate icons.
    TODO

    use brenfbx.core.bfData.FbxTypeClassIdTree

    maybe shade items darker if one of their parents is disabled?

    """

    kFbxClassRole = Qt.QtCore.Qt.UserRole

    def __init__(self, parent=None, fbx_manager=None, data_root=None):
        super(BFbxClassIdBoolTreeModel, self).__init__(parent=parent)

        if data_root is None:
            # fbx manager must be instanced to manage FbxClassId objects
            if fbx_manager is None:
                fbx_manager = fbx.FbxManager.Create()

            data_root = bfData.FbxClassIdBoolRoot(fbx_manager)

        self.set_data_root(data_root)

#         self.data.debug()

    def data_root(self):
        return self._data_root

    def set_data_root(self, data_root):
        """
        TODO checks
        """
        self.beginResetModel()
        self._data_root = data_root
        self.endResetModel()

    def serialize(self, as_json=True, pretty=True):
        return self.data_root.serialize(
            as_json=as_json, pretty=pretty
        )

    def deserialize(self, str_data):
        self.beginResetModel()
        res = self._data_root.deserialize(str_data)
        self.endResetModel()
        return res

    def get_item(self, index):
        item = index.internalPointer()
        return item

    def index(self, row, column, parent_index):
        """
        """

        if not parent_index.isValid():
            parent_item = self._data_root
        else:
            parent_item = self.get_item(parent_index)

        item = parent_item.get_child(row)

        index = self.createIndex(row, column, item)

        return index

    def parent(self, index):
        if not index.isValid():
            return Qt.QtCore.QModelIndex()

        item = self.get_item(index)
        parent_item = item.parent()

        if parent_item is self._data_root:
            return Qt.QtCore.QModelIndex()
        else:

            return self.createIndex(
                parent_item.index(), 0, parent_item
            )

    def rowCount(self, index):
        if not index.isValid():
            item = self._data_root
        else:
            item = self.get_item(index)

        return item.child_count()

    def columnCount(self, index):
        return 1

    def flags(self, index):
        """ hard-coded item flags """

        return Qt.QtCore.Qt.ItemIsUserCheckable | Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        """

        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        item = self.get_item(index)

        return BFbxClassIdBoolListModel.get_item_data(item, role)

    def setData(self, index, value, role):

        if not index.isValid():
            return

        item = self.get_item(index)

        res = BFbxClassIdBoolListModel.set_item_data(item, value, role)

#         self._data_root.debug()

        return res


if __name__ == "__main__":

    app = Qt.QtWidgets.QApplication(sys.argv)

    if False:
        view = Qt.QtWidgets.QListView()
        model = BFbxTypeModel()
        view.setModel(model)
        view.show()
    elif False:
        fbx_manager = fbx.FbxManager.Create()
        data = bfData.FbxClassIdBoolRoot(fbx_manager)
        data.debug()
    elif False:
        # TODO check is still working?
        view = Qt.QtWidgets.QListView()
        model = BFbxClassIdBoolListModel()
        view.setModel(model)
    elif True:
        # TODO seems to lose track when clicking quickly?
        view = Qt.QtWidgets.QTreeView()
        model = BFbxClassIdBoolTreeModel()
        view.setModel(model)
        view.expandAll()

        view.show()

    sys.exit(app.exec_())
