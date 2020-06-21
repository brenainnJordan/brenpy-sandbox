'''

** WIP **

'''

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
from brenfbx.fbxsdk.core import bfProperty

from brenfbx.qt import bfQtCore, bfSceneQtCache
from brenfbx.qt import bfPropertyQtCache
from brenfbx.qt import bfIcons


class BFbxPropertyModel(bpQtCore.BpAbstractItemModel):
    """
    Models all properties for all objects in the scene.
    """

    kFbxPropertyRole = Qt.QtCore.Qt.UserRole
    kFbxObjectRole = Qt.QtCore.Qt.UserRole + 1
    kPathNameRole = Qt.QtCore.Qt.UserRole + 2
    kPathNameStrRole = Qt.QtCore.Qt.UserRole + 3

    COLUMNS = [
        "name",
        "value",
        "fnType",
        "type",
    ]

    def __init__(self, scene_model, parent=None):
        super(BFbxPropertyModel, self).__init__(parent)

        self._print_warnings = True

        self._scene_model = None

        # TODO use class instead of tuple
        self._columns = self.COLUMNS

        if scene_model is not None:
            self.set_scene_model(scene_model)

    def warning(self, msg):
        if self._print_warnings:
            print msg

    def scene_model(self):
        return self._scene_model

    def scene_cache(self):
        if self._scene_model is None:
            return None

        return self._scene_model.scene_cache()

    def set_scene_model(self, scene_model):
        """Reset model"""

        self.beginResetModel()
        self._scene_model = scene_model
        self.endResetModel()

    def get_fbx_property_id(self, value):

        property_id = None

        if isinstance(value, Qt.QtCore.QModelIndex):

            id_object = value.internalPointer()

            if isinstance(id_object, bfPropertyQtCache.BfPropertyId):
                property_id = id_object.value()
            else:
                self.warning(
                    "Pointer not BfPropertyId: {}".format(id_object)
                )

        elif isinstance(value, bfPropertyQtCache.BFbxPropertyRoot):
            property_id = value.unique_id()

        elif isinstance(value, bfPropertyQtCache.BfPropertyId):
            property_id = value.value()

#         elif isinstance(value, (int, long)):
#             property_id = value

        else:
            property_id = None

        if property_id is None:

            raise bfQtCore.BfQtError(
                "Failed to retrieve fbx property id: {}".format(value)
            )

        return property_id

    def get_fbx_object_id(self, value):

        fbx_object_id = None

        if isinstance(value, Qt.QtCore.QModelIndex):

            id_object = value.internalPointer()

            if isinstance(id_object, bfPropertyQtCache.BfPropertyId):
                fbx_object_id = id_object.fbx_object_id()

            elif isinstance(id_object, bfSceneQtCache.BfIdData):
                fbx_object_id = id_object.value()

            else:
                self.warning(
                    "Pointer not BfPropertyId or BfIdData: {}".format(
                        id_object
                    )
                )

        elif isinstance(value, bfPropertyQtCache.BFbxPropertyRoot):
            fbx_object_id = value.fbx_object().GetUniqueID()

#         elif isinstance(value, (int, long)):
#             fbx_object_id = value
        elif isinstance(value, bfPropertyQtCache.BfPropertyId):
            fbx_object_id = value.fbx_object_id()

        elif isinstance(value, bfSceneQtCache.BfIdData):
            fbx_object_id = value.value()

        else:
            fbx_object_id = None

        if fbx_object_id is None:

            raise bfQtCore.BfQtError(
                "Failed to retrieve fbx object id: {}".format(value)
            )

        return fbx_object_id

    def get_property_cache(self, value):

        fbx_object_id = self.get_fbx_object_id(value)

        property_cache = self.scene_cache().get_property_cache(
            fbx_object_id
        )

        return property_cache

#     def get_fbx_object(self):
#
#         if self._scene_model is None:
#             return None
#
#         return self._scene_model.scene_cache().id_data[
#             self._fbx_object_id
#         ]

    def get_property_root(self, value):
        if self._scene_model is None:
            return None

        property_cache = self.get_property_cache(value)
        property_root = property_cache.root()

        return property_root

    def get_property_item(self, value):

        property_id = self.get_fbx_property_id(value)

        property_cache = self.get_property_cache(value)

        item = property_cache.get_item_from_unique_id(
            property_id
        )

        return item

    def get_fbx_property(self, value):
        item = self.get_property_item(value)
        return item.fbx_property()

    def get_id_object(self, value):

        property_cache = self.get_property_cache(value)

        id_object = property_cache.get_id_object(value)

        return id_object

    def get_id_con_object(self, value):

        property_cache = self.get_property_cache(value)

        id_con_object = property_cache.get_id_con_object(value)

        return id_con_object

    def get_root_row(self, value):
        """Find row suitable for root property.

        Find index from scene cache objects.

        """
        if isinstance(value, (int, long)):
            fbx_object_id = value

        elif isinstance(value, bfPropertyQtCache.BFbxPropertyRoot):
            fbx_object_id = value.fbx_object().GetUniqueID()

        else:
            raise bfQtCore.BfQtError(
                "Cannot get root row from value: {}".format(value)
            )

        root_row = self.scene_cache().id_list.index(fbx_object_id)

        return root_row

    def get_root_index(self, value):

        row = self.get_root_row(value)

        root_index = self.index(
            row,
            0,
            Qt.QtCore.QModelIndex()
        )

        return root_index

    def parent(self, index):
        """Create an index for parent object of requested index.
        """

        if not index.isValid():
            #             return None
            # TODO raise?
            return Qt.QtCore.QModelIndex()

        item = self.get_property_item(index)

        if item is None:
            raise bfQtCore.BfQtError(
                "No item found, cannot get parent: {}".format(index)
            )

            return None
            # TODO raise?
            return Qt.QtCore.QModelIndex()

        if item.is_root():
            # return invalid index to indicate root level
            return Qt.QtCore.QModelIndex()

        parent_item = item.parent()

        if parent_item.is_root():

            parent_row = self.get_root_row(parent_item)

        else:
            parent_row = parent_item.get_index()

        parent_column = 0

        data = self.get_id_object(parent_item)

        if data is None:
            raise bfQtCore.BfQtError(
                "Failed to retreive id_object for parent item: {}".format(
                    parent_item
                )
            )

        parent_index = self.createIndex(
            parent_row, parent_column, data
        )

        if not parent_index.isValid():
            raise Exception("fuuuuck")

        return parent_index

    def index(self, row, column, parent_index):
        """
        TODO implement dummy system, similar to scene model
        to help manage property hierarchy.

        Can use FbxProperty.GetParent()

        OR use GetClassRootProperty()/GetChild()/GetSibling()

        TODO check why is not valid in fbx_property_hierarchy example 

        """

        if not parent_index.isValid():
            # root level
            fbx_object_id = self.scene_cache().id_list[row]
            id_object = self.scene_cache().get_id_object(fbx_object_id)

            property_cache = self.get_property_cache(id_object)

            property_item = property_cache.root()

        else:
            parent_item = self.get_property_item(parent_index)

            if row > parent_item.child_count():
                print "DEBUG: out of range: {}/{} {}".format(
                    row, parent_item.child_count(), self.rowCount(parent_index)
                )
                return None

            property_item = parent_item.get_child(row)

        data = self.get_id_object(property_item)

        if data is None:
            raise bfQtCore.BfQtError(
                "Failed to retreive id_object for item: {}".format(
                    property_item)
            )

        index = self.createIndex(row, column, data)

        if not index.isValid():
            raise Exception("index fuuuuck")

        return index

    def rowCount(self, index):
        if self.scene_cache() is None:
            return 0

        if not index.isValid():
            # root level
            return len(self.scene_cache().id_list)

        else:

            item = self.get_property_item(index)

            if item is None:
                return 0

            return int(item.child_count())

    def columnCount(self, index=None):
        return len(self._columns)

    def data(self, index, role):
        """
        TODO add decoration role for reference object icons!
        """

        prop_item = self.get_property_item(index)

        if prop_item is None:
            return None

        if role == self.kFbxObjectRole:
            return prop_item.fbx_object()

        elif role == self.kFbxPropertyRole:
            return prop_item.fbx_property()

        elif role == self.kPathNameRole:
            return [
                str(i.GetName()) for i in
                prop_item.fbx_object(), prop_item.fbx_property()
            ]

        elif role == self.kPathNameStrRole:
            name_path = self.data(index, self.kPathNameRole)
            return ".".join(name_path)

        if prop_item.is_root():
            data = self._get_root_item_data(index.column(), role, prop_item)

        else:
            data = self._get_prop_fn_data(index.column(), role, prop_item)

        return data

    def _get_root_item_data(self, column, role, root_item):

        #         if role == self.kPathNameRole:
        #             return [
        #                 str(root_item.fbx_object().GetName())
        #             ]

        if column == 0:
            if role in [Qt.QtCore.Qt.DisplayRole]:
                return str(
                    root_item.fbx_property().GetName()
                )

        return None

    def _get_prop_fn_data(self, column, role, prop_item):

        #         if role == self.kPathNameRole:
        #             return [
        #                 str(i.GetName()) for i in
        #                 prop_item.fbx_object(), prop_item.fbx_property()
        #             ]

        prop_fn = prop_item.property_object()

        if prop_fn is None:
            return None

        if role in [Qt.QtCore.Qt.DisplayRole, Qt.QtCore.Qt.EditRole]:
            if column == 0:
                return str(prop_fn.GetName())

            elif column == 1:

                if isinstance(prop_fn, bfProperty.InputReferenceProperty):
                    ref_object = prop_fn.Get()

                    if ref_object is None:
                        return ""

                    return ref_object.GetName()

                elif isinstance(prop_fn, bfProperty.InputReferenceArrayProperty):
                    return None

                elif isinstance(prop_fn, bfProperty.FSEnumProperty):
                    return prop_fn.GetStr()

                else:
                    return bfFbxUtils.get_property_value_as_str(
                        prop_fn.CastProperty()
                    )
            elif column == 2:
                #                 return str(type(prop_fn))
                return prop_fn.__class__.__name__

            elif column == 3:
                return prop_fn.GetTypeStr()
            else:
                return None

        if role in [Qt.QtCore.Qt.DecorationRole]:
            if column == 1:
                if isinstance(prop_fn, bfProperty.InputReferenceProperty):

                    ref_object = prop_fn.Get()

                    if ref_object is None:
                        return ""

                    return bfIcons.get_fbx_object_icon(ref_object)

        return None

    def setData(self, index, value, role=Qt.QtCore.Qt.EditRole):
        """
            ** overide method **

            Called with EditRole by view when user enters text into specified QModelIndex

            :param index QModelIndex
            :param value QVariant
            :param role int (Qt.QtCore.Qt namespace enum)

        """

        if not index.isValid():
            return False

        prop_item = self.get_property_item(index)

        if prop_item is None:
            return False

        result = self._set_prop_fn_data(
            index, role, prop_item, value
        )

        return result

    def _set_prop_fn_data(self, index, role, prop_item, value):
        """

        ** WIP refactoring **

        """
        row = index.row()
        column = index.column()

        # for now limit editing data to value only (column 1)
        if column != 1:
            return

        prop_fn = prop_item.property_object()

        if prop_fn is None:
            return

        if role == Qt.QtCore.Qt.EditRole:

            if isinstance(prop_fn, bfProperty.InputReferenceProperty):
                print "setting ref: {}".format(value.GetName())

                prop_fn.Set(value)

#                 if isinstance(value, brObject.FbxObjectFunctionSet):
#                     prop_fn.Set(value)
#                 else:
#                     return False
            elif isinstance(prop_fn, bfProperty.InputReferenceArrayProperty):
                return False

            elif isinstance(prop_fn, bfProperty.FSEnumProperty):
                # enums should be settable from enum str value
                prop_fn.Set(value)

            else:

                value = bfFbxUtils.get_property_value_from_str(
                    prop_fn.Property(),
                    value
                )

                prop_fn.Set(value)

            self.dataChanged.emit(index, index)

            return True

        return False

    def flags(self, index):
        """ hard-coded item flags """

        if index.column() == 1:
            return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable | Qt.QtCore.Qt.ItemIsEditable
        else:
            return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

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
        raise NotImplementedError()

    def insertColumns(self, *args, **kwargs):
        raise NotImplementedError()

    def insertRow(self, *args, **kwargs):
        """TODO add property button!"""
        raise NotImplementedError()

    def insertRows(self, *args, **kwargs):
        raise NotImplementedError()

    def _clear(self):
        self.beginResetModel()
        self._scene_model = None
        self.endResetModel()

    def deleteLater(self):
        """Disconnect all references, for clean deletion.
        """
        self._clear()
        super(BFbxPropertyModel, self).deleteLater()
