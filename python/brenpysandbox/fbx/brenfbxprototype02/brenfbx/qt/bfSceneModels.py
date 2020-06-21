'''

TODO Notes:
item delegates is not going to work for our modifier widgets
(because of the issue with persistent editors)

Meaning we can't display a list of modifier widgets with the properties of an object.
(at least not using model/view objects)

Instead we can simply show a list of modifiers under the properties,
with completion classes to keep things in sync nicely.

To see the properties of each modifier, the user will either need to navigate to the modifier
in the scene view and select it to only show properties for that object,
and/or provide a context menu from the list of modifiers on another object
to select that modifier object for convenience.


Item delegates may still be useful however for enforcing limits or providing
convenience for setting data in a view etc.

'''

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

from brenpy.qt import bpQtCore

from brenfbx.utils import bfFbxUtils
from brenfbx.core import bfCore

from brenfbx.qt import bfPropertyModels
from brenfbx.qt import bfSceneQtCache

from brenfbx.qt import bfIcons


class BFbxSceneTreeQtModel(bpQtCore.BpAbstractItemModel):
    """Model uses all scene connections and children for all nodes.
    Uses dummy indexes to avoid duplication.
    """
    # define custom role enums for returning specific data to sort by
    #     kSortRole = Qt.QtCore.Qt.UserRole
    kFilterRole = Qt.QtCore.Qt.UserRole + 1
    kFbxClassIdRole = Qt.QtCore.Qt.UserRole + 2
    kFbxObjectRole = Qt.QtCore.Qt.UserRole + 3
    kPathNameRole = Qt.QtCore.Qt.UserRole + 4
    kPathNameStrRole = Qt.QtCore.Qt.UserRole + 5

    COLUMNS = [
        "name",
        "type",
        "ID",
        "pixmap",
        "icon",
    ]

    def __init__(self, parent=None):
        super(BFbxSceneTreeQtModel, self).__init__(parent)

        self._scene = None
        self._fbx_manager = None
        self._scene_cache = None
#         self._property_models = {}
        self._property_model = None

        self._headers = self.COLUMNS

    def get_fbx_object_id(self, index):
        """TODO checks

            - check index belongs to model!

        """
        data = index.internalPointer()

        # for example in the case of an invalid index
        if data is None:
            print "No FbxObject ID data found: {}".format(index)
            return None

        # get id object
        object_id = data.value()

        return object_id

    def get_fbx_object(self, value):
        """TODO checks
        """

        if isinstance(value, Qt.QtCore.QModelIndex):
            object_id = self.get_fbx_object_id(value)
        else:
            object_id = value

        if object_id not in self._scene_cache.id_data:
            raise bfCore.BfError(
                "Object ID not found: {}".format(object_id)
            )

        fbx_object = self._scene_cache.id_data[object_id]

        return fbx_object

    def get_fbx_nodes(self, indices):
        """Get list of FbxNodes from indices.

        Note: for some reason list comparison fails with nodes
        so compare using ids instead to get unique list.

        """

        nodes = []
        ids = []

        for index in indices:
            object_id = self.get_fbx_object_id(index)

            if object_id in ids:
                continue

            fbx_object = self.get_fbx_object(index)

            if isinstance(fbx_object, fbx.FbxNode):
                nodes.append(fbx_object)
                ids.append(object_id)

        return nodes

    def is_dummy(self, index):
        """Checks if index contains a BfIdDummyData object.
        """
        data = index.internalPointer()
        is_dummy = isinstance(data, bfSceneQtCache.BfIdDummyData)

        return is_dummy

    def parent(self, index):
        """Create an index for parent object of requested index.
        # TODO somethings broke!
        """

        if not index.isValid():
            return Qt.QtCore.QModelIndex()

        # dummy indexes are always at model root level
        if self.is_dummy(index):
            return Qt.QtCore.QModelIndex()

        # get the node stored in this index
        fbx_object = self.get_fbx_object(index)

        if isinstance(fbx_object, fbx.FbxNode):
            # child level
            parent_object = fbx_object.GetParent()

            if parent_object is None:
                return Qt.QtCore.QModelIndex()
            else:
                parent_id = parent_object.GetUniqueID()

                parent_row = bfFbxUtils.get_fbx_node_index(parent_object)

                # if we are at scene level
                # we need to find a suitable row
                if parent_row is None:
                    if parent_id in self.scene_cache().id_list:
                        parent_row = self.scene_cache().id_list.index(parent_id)
                    else:
                        return Qt.QtCore.QModelIndex()

                # create a new index with pointer to our parent node
                # (row, column, object to point to)

                parent_column = 0

                # get uid object from cache
                data = self._scene_cache.id_objects[parent_id]

                if data is None:
                    print "warning no id found: {} {}".format(
                        parent_id, fbx_object.GetName()
                    )
                    return Qt.QtCore.QModelIndex()

                parent_index = self.createIndex(
                    parent_row, parent_column, data
                )

                return parent_index

        return Qt.QtCore.QModelIndex()

    def get_id_object(self, object_id):

        id_object = self.scene_cache().get_id_object(object_id)

        return id_object

    def get_id_dummy_object(self, object_id):

        id_con_object = self.scene_cache().get_id_dummy_object(object_id)

        return id_con_object

    def get_id_con_object(self, object_id):

        id_con_object = self.scene_cache().get_id_con_object(object_id)

        return id_con_object

    def index(self, row, column, parent_index):
        """

        """

        if not parent_index.isValid():

            object_id = self._scene_cache.id_list[row]
            fbx_object = self._scene_cache.id_data[object_id]

            data = self.get_id_object(object_id)

            # if we are at model root level
            # and we are looking for a node that is a child
            # we should return dummy data to avoid duplicates
            if isinstance(fbx_object, fbx.FbxNode):
                if fbx_object.GetParent() is not None:
                    data = self.get_id_dummy_object(object_id)

        else:
            parent_object = self.get_fbx_object(parent_index)

            if isinstance(parent_object, fbx.FbxNode):

                child_id = parent_object.GetChild(row).GetUniqueID()
                fbx_object = self._scene_cache.id_data[child_id]
                data = self.get_id_object(child_id)

            else:
                data = None

        if data is None:
            print "warning no id found: {} {}".format(
                object_id, fbx_object.GetName()
            )
            return Qt.QtCore.QModelIndex()

        index = self.createIndex(row, column, data)

        return index

    def rowCount(self, index):
        """Return number of (non dummy) FbxNode children or 0 for anything else.
        """
        # dummy indexes should have no children
        if self.is_dummy(index):
            return 0

        if self.scene_cache() is None:
            return 0

        if not index.isValid():
            # if index is not valid, then we must be at root level
            return len(self.scene_cache().id_list)

        else:
            fbx_object = self.get_fbx_object(index)

            if isinstance(fbx_object, fbx.FbxNode):
                return fbx_object.GetChildCount()

        return 0

    def columnCount(self, index=None):
        return len(self._headers)

    def data(self, index, role):
        """
            ** overide method **

            Called by view to get data for specified QModelIndex for specified role
        """

        if not index.isValid():
            return

        # we don't want to lose sync with child objects
        # so always return proxy name for dummy indexes
        if self.is_dummy(index):
            if role in [Qt.QtCore.Qt.DisplayRole, self.kPathNameStrRole]:
                return "DUMMY"
            else:
                return None

        row = index.row()
        column = index.column()

        object_id = self.get_fbx_object_id(index)

        return self.get_fbx_object_data(object_id, column, role)

    def get_fbx_object_data(self, object_id, column, role):
        """Stuff"""

        fbx_object = self.get_fbx_object(object_id)

        name = str(fbx_object.GetName())

        if role in [Qt.QtCore.Qt.DisplayRole, Qt.QtCore.Qt.EditRole]:

            if column == 0:
                return name
            elif column == 1:
                return str(type(fbx_object).__name__)
#                 name = str(fbx_object.__class__.__name__)
#                 return get_fbx_node_attribute_label(node)
            elif column == 2:
                return fbx_object.GetUniqueID()
            elif column == 3:
                return bfIcons.get_fbx_object_pixmap(fbx_object, scale=(15, 15))
            elif column == 4:
                return bfIcons.get_fbx_object_icon(fbx_object)
            else:
                return "null"

        elif role in [Qt.QtCore.Qt.DecorationRole]:
            if column == 0:
                return bfIcons.get_fbx_object_icon(fbx_object)

        # filter by name
        elif role == BFbxSceneTreeQtModel.kFilterRole:
            return name

        elif role == BFbxSceneTreeQtModel.kFbxClassIdRole:
            return fbx_object.ClassId

        elif role == BFbxSceneTreeQtModel.kFbxObjectRole:
            return fbx_object

        elif role == BFbxSceneTreeQtModel.kPathNameRole:
            # TODO
            return [str(fbx_object.GetName())]

        elif role == self.kPathNameStrRole:
            name_path = self.get_fbx_object_data(
                object_id, column, self.kPathNameRole
            )

            return "|".join(name_path)
        else:
            return None

    def setData(self, index, value, role=Qt.QtCore.Qt.EditRole):
        """
            ** overide method **

            Called with EditRole by view when user enters text into specified QModelIndex

            :param index QModelIndex
            :param value QVariant
            :param role int (Qt.QtCore.Qt namespace enum)

        """
        # we never want to set data for dummy indexes
        if self.is_dummy(index):
            return False

        if not index.isValid():
            return False

        row = index.row()
        column = index.column()

        fbx_object = self.get_fbx_object(index)
        object_id = fbx_object.GetUniqueID()

        # prevent user from renaming session or session rows
        if fbx_object is self._scene:
            return False

        # rename object
        if role == Qt.QtCore.Qt.EditRole:
            if column == 0:
                fbx_object.SetName(value)
                print "Edited: ", value, fbx_object.GetName()
            else:
                pass

            self.dataChanged.emit(index, index)

            return True

        return False

    def flags(self, index):
        """ hard-coded item flags """

        if self.is_dummy(index):
            return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

        if not index.isValid():
            return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

        fbx_object = self.get_fbx_object(index)
        object_id = fbx_object.GetUniqueID()

        if fbx_object is self._scene.GetRootNode():
            return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

        # return editable
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable | Qt.QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        return self.header_data(section, orientation, role)

    @classmethod
    def header_data(cls, section, orientation, role):
        if role == Qt.QtCore.Qt.DisplayRole:
            if orientation == Qt.QtCore.Qt.Horizontal:
                if section < len(cls.COLUMNS):
                    return cls.COLUMNS[section]
                else:
                    return "other"

    def insertColumn(self, *args, **kwargs):
        raise NotImplementedError("Use addNode or createNode instead")

    def insertColumns(self, *args, **kwargs):
        raise NotImplementedError("Use addNodes or createNodes instead")

    def insertRow(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNode instead")

    def insertRows(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNodes instead")

    def removeRow(self, row, parent_index):
        """
        TODO
        """

        # find fbx_object
        fbx_object = self.get_fbx_object(
            self.index(row, 0, parent_index)
        )

        if fbx_object is None:
            print "Cannot delete: {} {}".format(row, parent_index)

        self.beginResetModel()
        self._parity_models.beginResetModels()

        self._scene_cache.delete_object(fbx_object)

#         self.reset_model()

        self.endResetModel()
        self._parity_models.endResetModels()

    def create_object(self, fbx_cls, name=None):
        """TODO use class id object instead
        """
        self.beginResetModel()
        self._parity_models.beginResetModels()

        fbx_object = self._scene_cache.create_object(
            fbx_cls, name=name
        )

#         self.create_property_model(fbx_object.GetUniqueID())

        print "done"
        self.endResetModel()
        self._parity_models.endResetModels()

    def delete_object(self, fbx_object):
        print "removing object: {}".format(fbx_object.GetName())
#         self.delete_property_model(fbx_object.GetUniqueID())
        self._scene_cache.delete_object(fbx_object)
        return True

    def removeIndices(self, indices):
        """
        TODO
        """

        # get objects to delete
        fbx_objects = set([])

        for index in indices:
            fbx_object = self.get_fbx_object(index)
            if fbx_object is not None:
                fbx_objects.add(fbx_object)

        self.beginResetModel()
        self._parity_models.beginResetModels()

        for fbx_object in fbx_objects:
            self.delete_object(fbx_object)

#         self.reset_model()
        print "done"
        self.endResetModel()
        self._parity_models.endResetModels()

    def add_node_children(self, indices):

        # get nodes
        nodes = self.get_fbx_nodes(indices)

        # check we have enough selected to continue
        if len(nodes) < 2:
            print "Not enough nodes selected to add children"
            return False

        # re-parent nodes
        self.beginResetModel()
        self._parity_models.beginResetModels()

        for child_node in nodes[:-1]:
            nodes[-1].AddChild(child_node)

        print "done"
        self.endResetModel()
        self._parity_models.endResetModels()

        return True

    def unparent_nodes(self, indices):
        # get nodes
        nodes = self.get_fbx_nodes(indices)

        # check we have enough selected to continue
        if not len(nodes):
            print "No nodes selected to unparent"
            return False

        # reparent nodes
        self.beginResetModel()
        self._parity_models.beginResetModels()

        for child_node in nodes:
            parent = child_node.GetParent()

            if parent is None:
                continue

            parent.RemoveChild(child_node)

        print "done"
        self.endResetModel()
        self._parity_models.endResetModels()

        return True

    def set_scene(self, fbx_scene, fbx_manager):
        self.beginResetModel()
        self._parity_models.beginResetModels()

        self._scene = fbx_scene
        self._fbx_manager = fbx_manager
        self.reset_model()

        self._parity_models.endResetModels()
        self.endResetModel()

    def reset_model(self):
        #         self.delete_property_model()
        self.create_scene_cache()
#         self.create_property_model()

    def delete_property_model(self):
        """Cleanly delete property model.
        """

        if self._property_model is None:
            return False

        self._property_model.deleteLater()
        self._property_model = None

        return True

    def create_property_model(self):
        """Create a property model including properties for all objects in the scene.

        NOTE
            Why is this neccessary?
            Would it not be simpler/cleaner to create these on demand?

            The idea is we could potentially have unknown views
            editing properties on the same fbx object, at unknown times.
            So "on demand" would not be suitable, as we could end up with
            multiple models, all out of sync with each other.

            Better to manage property editing via a single shared property model.

        TODO notes on using single property model over one per object...

        """

        self._property_model = bfPropertyModels.BFbxPropertyModel(
            self,
            parent=self
        )

    def property_model(self):
        return self._property_model

    def create_scene_cache(self):
        """Create a temporary cache of entire scene in a custom object.
        Where key is object UID and value is FbxObject.
        """
        try:
            self._scene_cache = bfSceneQtCache.BFbxSceneCache(
                self._scene, self._fbx_manager
            )
        except:
            print "arse"
            raise
            self._scene_cache = None

    def scene_cache(self):
        return self._scene_cache


class BFbxSceneDummyFilterModel(
        #         BFbxSortFilterProxyModel
    bpQtCore.BpSortFilterProxyModel
):
    """Allows parents of filtered row to remain visible.

    https://stackoverflow.com/questions/250890/using-qsortfilterproxymodel-with-a-tree-model

    ** WIP **
    """

    def __init__(self, *args, **kwargs):
        super(BFbxSceneDummyFilterModel,
              self).__init__(*args, **kwargs)

    def filterAcceptsRow(self, source_row, source_parent):
        src_index = self.sourceModel().index(source_row, 0, source_parent)

#         if self.sourceModel().is_dummy(src_index):
        if self.get_root_model().is_dummy(src_index):
            return False
        else:
            return True
#
#     def set_fbx_scene(self, fbx_scene):
#         self.sourceModel().set_fbx_scene(fbx_scene)
#         self.update()
#
#     def update(self):
#         self.sourceModel().update()

#
# class BFbxSceneTableQtModel(Qt.QtCore.QAbstractItemModel):
#     """Custom model to access data on all objects in the scene.
#     Model has no hierarchical information.
#
#     ** potentially redundant? **
#
#     """
#     # define custom role enums for returning specific data to sort by
#     #     kSortRole = Qt.QtCore.Qt.UserRole
#     kFilterRole = Qt.QtCore.Qt.UserRole + 1
#
#     def __init__(self, parent=None):
#         super(BFbxSceneTableQtModel, self).__init__(parent)
#
#         self._scene = None
#         self._scene_cache = None
#         self._property_models = {}
#
#         self._headers = [
#             "name",
#             "type",
#             "ID",
#             "pixmap",
#             "icon",
#         ]
#
#     def index(self, row, column, parent_index):
#         """
#
#         """
#
#         # redundant fail-safes
#         if parent_index.isValid():
#             return Qt.QtCore.QModelIndex()
#
#         if row > self.rowCount(parent_index):
#             return Qt.QtCore.QModelIndex()
#
#         # get corresponding FbxObject
#         object_id = self._scene_cache.id_list[row]
#         fbx_object = self._scene_cache.id_data[object_id]
#
#         index = self.create_index(row, column, fbx_object)
#
#         return index
#
#     def create_index(self, row, column, fbx_object):
#         """Create new index with pointer to desired FbxObject
#         use id object from cache
#         """
#         object_id = fbx_object.GetUniqueID()
#         data = self._scene_cache.get_id_object(object_id)
#
#         if data is None:
#             print "warning no id found: {} {}".format(
#                 object_id, fbx_object.GetName()
#             )
#             return Qt.QtCore.QModelIndex()
#
#         index = self.createIndex(row, column, data)
#
#         return index
#
#     def parent(self, index):
#         """Model represents flat list, so no index should have parent.
#         Always returns invalid index.
#         """
#         return Qt.QtCore.QModelIndex()
#
#     def get_fbx_object(self, index):
#         """TODO checks
#         """
#         data = index.internalPointer()
#
#         # for example in the case of an invalid index
#         if data is None:
#             if False:
#                 print "No FbxObject ID data found: {}".format(index)
#                 return None
#             else:
#                 raise Exception("No FbxObject ID data found: {}".format(index))
#
#         # get id object
#         object_id = data.value()
#
#         if object_id not in self._scene_cache.id_data:
#             raise bfCore.BFbxError("Object ID not found: {}".format(object_id))
#
#         fbx_object = self._scene_cache.id_data[object_id]
#
#         return fbx_object
#
#     def headerData(self, section, orientation, role):
#         """ called by view when naming rows and columns
#         """
#         if role == Qt.QtCore.Qt.DisplayRole:
#
#             if orientation == Qt.QtCore.Qt.Horizontal:
#                 if section < len(self._headers):
#                     return self._headers[section]
#                 else:
#                     return "Other {}".format(section)
#             else:
#                 return "{}".format(section)
#
#     def rowCount(self, parent_index=Qt.QtCore.QModelIndex()):
#         """ called by view to know how many rows to create
#         """
#         # we should only be querying root level
#         if not parent_index.isValid():
#             return len(self._scene_cache.id_list)
#         else:
#             return 0
#
#     def columnCount(self, parent=Qt.QtCore.QModelIndex()):
#         return len(self._headers)
#
#     def data(self, index, role):
#         """
#             called by view when populating item field
#
#             http://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
#
#         TODO implement custom id_role, icon_role, pixmap_role etc
#         """
#
#         row = index.row()
#         column = index.column()
#
#         fbx_object = self.get_fbx_object(index)
#
#         if fbx_object is None:
#             return None
#
#         name = str(fbx_object.GetName())
#
#         if role in [Qt.QtCore.Qt.DisplayRole, Qt.QtCore.Qt.EditRole]:
#
#             if column == 0:
#                 return name
#             elif column == 1:
#                 return str(type(fbx_object).__name__)
#             elif column == 2:
#                 return int(fbx_object.GetUniqueID())
#             elif column == 3:
#                 return bfIcons.get_fbx_object_pixmap(fbx_object, scale=(15, 15))
#             elif column == 4:
#                 return bfIcons.get_fbx_object_icon(fbx_object)
#             else:
#                 return "null"
#
#         if role in [Qt.QtCore.Qt.DecorationRole]:
#             if column == 0:
#                 return bfIcons.get_fbx_object_icon(fbx_object)
#
# #         if role == Qt.QtCore.Qt.FontRole:
# #             # not called by comboBox?
# #             return Qt.QtGui.QFont("Ariel", 20)
# #
# #         if role == Qt.QtCore.Qt.TextAlignmentRole:
# #             # not called by comboBox?
# #             return Qt.QtCore.Qt.AlignmentFlag.AlignCenter
#
# #         if role == Qt.QtCore.Qt.BackgroundRole:
# #             return color
#
# #         if role == Qt.QtCore.Qt.ToolTipRole:
# #             return "Hex code: " + color.name()
#
#     def flags(self, index):
#         """Per index flags
#         """
#         row = index.row()
#         column = index.column()
#
#         # only allow name to be editable
#         if column != 0:
#             return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable
#
#         fbx_object = self.get_fbx_object(index)
#
#         if fbx_object is None:
#             return None
#
#         object_id = fbx_object.GetUniqueID()
#
#         # prevent user from editing root node
#         if fbx_object is self._scene_cache.root_node:
#             return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable
#
#         if fbx_object is self._scene:
#             return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable
#
#         # return editable
#         return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable | Qt.QtCore.Qt.ItemIsEditable
#
#     def setData(self, index, value, role=Qt.QtCore.Qt.EditRole):
#         """
#         """
#
#         if not index.isValid():
#             return False
#
#         row = index.row()
#         column = index.column()
#
#         fbx_object = self.get_fbx_object(index)
#         object_id = fbx_object.GetUniqueID()
#
#         # safeguard against editing anything other than name
#         if column != 0:
#             return False
#
#         # prevent user from renaming protected objects
#         # TODO list protected object ids in cache
#         if fbx_object is self._scene_cache.root_node:
#             return False
#
#         if fbx_object is self._scene:
#             return False
#
#         # rename object
#         if role == Qt.QtCore.Qt.EditRole:
#             old_name = fbx_object.GetName()
#
#             fbx_object.SetName(value)
#
#             print "FbxObject name changed from {} to {}, new name: {}".format(
#                 old_name, value, fbx_object.GetName()
#             )
#
#             self.dataChanged.emit(index, index)
#
#             return True
#
#         return False
#
#     def insertRows(self, position, row_count, parent=Qt.QtCore.QModelIndex()):
#         """ parent is ignored, will be used for tree view later
#         """
#
#         # send signal to views that were are about to modify the following rows
#         # (parent, first row, last row)
#         self.beginInsertRows(parent, position, position + row_count - 1)
#
# #         for _ in range(row_count):
# #             # insert default values into our list
# #             default_values = [QtGui.QColor("#000000")] * self.columnCount(None)
# #             self._colors.insert(position, default_values)
#
#         # send a signal to views that we are done editing and to update items
#         self.endInsertRows()
#
#     def insertColumns(self, position, column_count, parent=Qt.QtCore.QModelIndex()):
#
#         self.beginInsertColumns(parent, position, position + column_count - 1)
#
# #         """
# #         #tutorial method
# #         for _ in range(column_count):
# #             for i in range(self.rowCount(None)):
# #                 self._colors[i].insert(position, QtGui.QColor("#000000"))
# #         """
# #
# #         for _ in range(column_count):
# #             for row in self._colors:
# #                 row.insert(position, Qt.QtGui.QColor("#000000"))
#
#         self.endInsertColumns()
#
#     def removeRows(self, position, row_count, parent=Qt.QtCore.QModelIndex()):
#         self.beginRemoveRows(parent, position, position + row_count - 1)
#
# #         for _ in range(row_count):
# #             self._colors.pop(position)
#
#         self.endRemoveRows()
#
#     def removeColumns(self, position, column_count, parent=Qt.QtCore.QModelIndex()):
#         self.beginRemoveColumns(parent, position, position + column_count - 1)
#
# #         for row in self._colors:
# #             for _ in range(column_count):
# #                 row.pop(position)
#
#         self.endRemoveColumns()
#
#     def set_scene(self, fbx_scene):
#         self.beginResetModel()
#         self._scene = fbx_scene
#         self.reset_model()
#         self.endResetModel()
#
#     def reset_model(self):
#         #         self.delete_property_fn_list_models()
#         self.create_scene_cache()
# #         self.create_property_fn_list_models()
#
#     def create_scene_cache(self):
#         """Create a temporary cache of entire scene in a custom object.
#         Where key is object UID and value is FbxObject.
#         """
#         try:
#             self._scene_cache = bfSceneQtCache.BFbxSceneCache(self._scene)
#         except:
#             print "arse"
#             raise
#             self._scene_cache = None
#
#     def scene_cache(self):
#         return self._scene_cache


class BFbxSceneHierarchyNameFilterModel(
        #         Qt.QtCore.QSortFilterProxyModel
    bpQtCore.BpSortFilterProxyModel
):
    """Allows parents of filtered row to remain visible.

    https://stackoverflow.com/questions/250890/using-qsortfilterproxymodel-with-a-tree-model

    ** WIP **

    ** REDUNDANT **
    (moved to bpQtCore)

    """

    HIGHLIGHT_COLOR = Qt.QtGui.QColor(200, 225, 255)

    def __init__(self, *args, **kwargs):
        super(
            BFbxSceneHierarchyNameFilterModel, self
        ).__init__(*args, **kwargs)

        self.setFilterCaseSensitivity(
            Qt.QtCore.Qt.CaseInsensitive
        )

        self.setFilterKeyColumn(0)

        self._highlighted_indices = set([])

    def data(self, index, role):
        """Override source model data method.

        Add background colour for highlighted indices.
        """

        if not index.isValid():
            return

        if role == Qt.QtCore.Qt.BackgroundRole:

            name = super(BFbxSceneHierarchyNameFilterModel, self).data(
                index, Qt.QtCore.Qt.DisplayRole
            )

            if name in self._highlighted_indices:
                return self.HIGHLIGHT_COLOR

        else:
            return super(BFbxSceneHierarchyNameFilterModel, self).data(index, role)

    def filterAcceptsRow(self, source_row, source_parent):
        # custom behaviour
        if not self.filterRegExp().isEmpty():
            # get source model index for current row
            source_index = self.sourceModel().index(
                source_row, self.filterKeyColumn(), source_parent)

            if source_index.isValid():
                # check current index
                key = self.sourceModel().data(source_index, self.filterRole())
                match = self.filterRegExp().exactMatch(key)

                if match:
                    name = self.sourceModel().data(source_index, Qt.QtCore.Qt.DisplayRole)
                    self._highlighted_indices.add(name)

                # recursively check children for matches
                # if any of children matches the filter, then current index
                # matches the filter as well

                row_count = self.sourceModel().rowCount(source_index)

                for i in range(row_count):
                    if self.filterAcceptsRow(i, source_index):
                        return True

                # return current match
                return match

        # parent call for default behaviour
        return super(BFbxSceneHierarchyNameFilterModel, self).filterAcceptsRow(source_row, source_parent)

#     def set_fbx_scene(self, fbx_scene):
#         self.sourceModel().set_fbx_scene(fbx_scene)
#         self.update()
#
#     def update(self):
#         self.sourceModel().update()


class BFbxSceneTypeFilterModel(bpQtCore.BpSortFilterProxyModel):
    """
    ** WIP **
    """

    def __init__(self, *args, **kwargs):
        super(BFbxSceneTypeFilterModel, self).__init__(*args, **kwargs)
        self._fbx_types = []

    def set_fbx_types(self, fbx_types):
        self.beginResetModel()
        self._fbx_types = fbx_types
        self.endResetModel()
        return True

    def filterAcceptsRow(self, source_row, source_parent):

        # get source model index for current row
        source_index = self.sourceModel().index(
            source_row, 0, source_parent
        )

        if source_index.isValid():
            class_id = self.sourceModel().data(
                source_index, BFbxSceneTreeQtModel.kFbxClassIdRole
            )

            if class_id in self._fbx_types:
                return True
            else:
                return False

        # parent call for default behaviour
        return super(BFbxSceneTypeFilterModel, self).filterAcceptsRow(
            source_row, source_parent
        )

#     def set_fbx_scene(self, fbx_scene):
#         self.sourceModel().set_fbx_scene(fbx_scene)
#         self.update()
#
#     def update(self):
#         self.sourceModel().update()


# class BFbxSceneChildFilterModel(Qt.QtCore.QSortFilterProxyModel):
#     """Removes any FbxNode that is a child of another FbxNode
#
#     *** redundant? ***
#
#     """
#
#     def __init__(self, *args, **kwargs):
#         super(BFbxSceneChildFilterModel, self).__init__(*args, **kwargs)
#
#     def filterAcceptsRow(self, source_row, source_parent):
#         source_index = self.sourceModel().index(
#             source_row, 0, source_parent
#         )
#
#         source_object = self.sourceModel().get_fbx_object(source_index)
#
#         if isinstance(source_object, fbx.FbxNode):
#             if source_object.GetParent() is not None:
#                 return False
#
#         return super(BFbxSceneChildFilterModel, self).filterAcceptsRow(
#             source_row, source_parent
#         )
