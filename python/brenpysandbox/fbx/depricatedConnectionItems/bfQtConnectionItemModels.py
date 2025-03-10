"""Dynamic item implementation for FbxConnections


** DEPRICATED **

See bfConnectionUtilityItems

"""

import brenfbx.test.bfTestBase
from brenpy.qt.core.bpQtImportUtils import QtCore
from brenpy.qt.core.bpQtImportUtils import QtWidgets

from brenpy.qt.item.models import bpQtItemsUndoModels

from brenfbx.qt.scene import bfQtSceneModels
from brenfbx.qt.property import bfQtPropertyModels
from brenfbx.items import bfConnectionItems

class BFbxConnectionsModelBase(
    brenfbx.core.bfEnvironment.BfEnvironmentDependant,
    bpQtItemsUndoModels.BpItemsUndoModel
):
    """
    TODO add undo support
    """
    # define custom role enums for returning specific data to sort by
    #     kSortRole = QtCore.Qt.UserRole
    # kFilterRole = QtCore.Qt.UserRole + 1
    # kFbxClassIdRole = QtCore.Qt.UserRole + 2
    # kFbxObjectRole = QtCore.Qt.UserRole + 3
    # kPathNameRole = QtCore.Qt.UserRole + 4
    # kPathNameStrRole = QtCore.Qt.UserRole + 5

    FBX_CONNECTED = QtCore.Signal()
    FBX_DISCONNECTED = QtCore.Signal()

    COLUMNS = [
        "name"
    ]

    def __init__(self, *args, **kwargs):
        super(BFbxConnectionsModelBase, self).__init__(*args, **kwargs)

        self.set_rebuild_on_refresh(True)

        self.set_drag_enabled(True)
        self.set_drop_enabled(True)

    def set_connected_obj(self, value):

        if self.item_manager() is None:
            return True

        self.beginResetModel()

        res = self.item_manager().set_connected_obj(value)

        self.endResetModel()

        return res

    def rowCount(self, index):
        """stuff"""

        if index.isValid():
            return 0

        if self.item_manager() is None:
            return 0

        row_count = self.item_manager().connection_count()

        return row_count
    #
    # def remove_rows(self, rows):
    #     """Disconnect specified row indices
    #     """
    #
    #     values = [self.get_connection(row) for row in rows]
    #
    #     for value in values:
    #         self.fbx_disconnect(value)
    #
    #     return True
    #
    # def removeIndices(self, indices):
    #     """
    #     wip
    #     """
    #
    #     if not len(indices):
    #         return False
    #
    #     rows = [i.row() for i in indices]
    #
    #     self.beginResetModel()
    #
    #     res = self.remove_rows(rows)
    #
    #     self.endResetModel()
    #
    #     return res

    def create_connection(self, value):
        """Create new connection
        """
        if self.item_manager() is None:
            return False

        self.beginResetModel()
        print "POOP model con", self.item_manager(), value
        res = self.item_manager().create_connection(value)

        self.endResetModel()

        self.FBX_CONNECTED.emit()

        return res

    def destroy_item(self, *args, **kwargs):
        res = super(BFbxConnectionsModelBase, self).destroy_item(*args, **kwargs)

        if not res:
            return res

        self.FBX_DISCONNECTED.emit()

        return res

    def fbx_disconnect_all(self):
        """Disconnect all source objects/properties
        """
        if self.item_manager() is None:
            return True

        self.beginResetModel()

        res = self.item_manager().fbx_disconnect_all()

        self.endResetModel()

        self.FBX_DISCONNECTED.emit()

        return res


class BFbxObjectConnectionsModelBase(BFbxConnectionsModelBase):
    """
    """

    COLUMNS = bfQtSceneModels.BfFbxSceneModel.COLUMNS

    def __init__(self, *args, **kwargs):
        super(BFbxObjectConnectionsModelBase, self).__init__(*args, **kwargs)

    @classmethod
    def create_default_icon_manager(cls):
        return bfQtSceneModels.BfFbxSceneModel.create_default_icon_manager()

    @classmethod
    def _get_item_data(cls, item, column, role, deligate_mode=False, icon_manager=None):

        # return bfQtSceneModels.BfFbxSceneModel._get_item_data(
        #     item, column, role, deligate_mode=False, icon_manager=icon_manager
        # )

        # TODO
        bf_object = None

        data = bfQtSceneModels.BfFbxSceneModel.get_bf_object_data(
            bf_object, column, role, icon_manager=icon_manager
        )

        return data


class BFbxPropertyConnectionsModelBase(BFbxConnectionsModelBase):
    """Base class for model looking for a connected property.
    """

    def __init__(self, *args, **kwargs):
        super(BFbxPropertyConnectionsModelBase, self).__init__(*args, **kwargs)

    @classmethod
    def _get_item_data(cls, item, column, role, deligate_mode=False, icon_manager=None):

        # data = bfQtPropertyModels.BfFbxPropertyModel._get_item_data(*args, **kwargs)

        # TODO
        fbx_property = None

        bf_environment = item.item_manager().bf_environment()

        if role in [QtCore.Qt.DisplayRole]:

            # return formatted property name
            data = "{}.{}".format(
                fbx_property.GetFbxObject().GetName(),
                fbx_property.GetName(),
            )

        else:
            if fbx_property.IsRoot():
                data = bfQtPropertyModels.BfFbxPropertyModel.get_fbx_root_property_data(
                    fbx_property, column, role
                )
            else:
                data = bfQtPropertyModels.BfFbxPropertyModel.get_fbx_property_data(
                    bf_environment, fbx_property, column, role, deligate_mode=False
                )

        return data


class Test1(object):
    def __init__(self, base):

        fbx_object = base._scene.GetRootNode()

        item_manager = bfConnectionItems.BfFbxSrcObjectsManager(bf_app=base.bf_environment())
        item_manager.set_debug_levels(item_manager.LEVELS.all())
        item_manager.set_connected_obj(fbx_object)

        item_manager.debug_hierarchy()

        model = BFbxObjectConnectionsModelBase(bf_app=base.bf_environment())
        model.set_item_manager(item_manager)

        self.view = QtWidgets.QTreeView()
        self.view.setModel(model)
        self.view.show()


if __name__ == "__main__":
    import os
    import sys

    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"

    app = QtWidgets.QApplication(sys.argv)

    base = brenfbx.test.bfTestBase.BfTestBase(file_path=os.path.join(DUMP_DIR, TEST_FILE))

    test = Test1(base)

    sys.exit(app.exec_())
