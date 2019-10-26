'''
stuff
'''

import sys

import os
import fbx
import FbxCommon
import inspect
from types import NoneType
from numpy import source

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

from brenpy.cg import bpEuler
from brenpy.utils import bpStr
from brenpy.qt import bpQtCore
from brenpy.qt import bpQtWidgets
from brenpy.qt.icons import icons8

from brenfbx.core import bfIO
from brenfbx.core import bfUtils
from brenfbx.core import bfCore
from brenfbx.core import bfData
from brenfbx.core import bfProperty
from brenfbx.core import bfObject

from brenfbx.qt import bfQtWidgets, bfSceneQtCache, bfQtCore
from brenfbx.qt import bfPropertyQtCache
from brenfbx.qt import bfIcons

from brenfbx.qt import bfSceneModels
from brenfbx.qt import bfPropertyModels


class BFbxSceneListProxyModel(bpQtCore.BpItemToListProxyModel):
    """Convert a scene tree model into flat list.
    """

    def __init__(self, parent=None):
        super(BFbxSceneListProxyModel, self).__init__(parent=parent)


class BFbxScenePropertiesProxyModel(Qt.QtCore.QAbstractProxyModel):
    """scene flat list proxy model including all properties as children.
    """

    def __init__(self, parent=None):
        """
        Instance dictionaries to hold property mappings.

        """
        super(BFbxScenePropertiesProxyModel, self).__init__(parent=parent)

        self._source_to_proxy_map = {}
        self._proxy_to_source_map = {}

        self._index_list = []

#         self._fbx_object_id_to_proxy_map = {}
#         self._fbx_object_id_to_source_map = {}
        self._fbx_object_id_to_row_map = {}

        # dictionaries of bpQtCore.IndexPath keys/objects.
        self._proxy_property_indices = {}

        # technically this dict is redundant but helps readability
        # we could simply use self._proxy_to_source_map instead
        self._proxy_to_source_property_map = {}

        # Key is fbx_object_id and value is dictionary
        # bpQtCore.IndexPath keys/objects.
#         self._source_to_proxy_property_map = {}

    def scene_model(self):
        return self.sourceModel()

    def is_scene_index(self, index, reject_dummys=True):
        """Test if proxy index or source index belongs to a scene model.
        """

        id_object = index.internalPointer()

        if isinstance(id_object, bfSceneQtCache.BfIdData):
            return True

        if isinstance(id_object, bfSceneQtCache.BfIdDummyData):
            if not reject_dummys:
                return True

        return False

    def is_property_index(self, index):
        """Test if proxy index or source index belongs to a property model
        """

        id_object = index.internalPointer()

        if isinstance(id_object, bfPropertyQtCache.BfPropertyId):
            return True
        else:
            return False

    def get_fbx_object_id(self, index):
        """Use IdObject to retreive objectId.

        Index can be either object or property index,
        and either proxy index or source index.
        """

        id_object = index.internalPointer()

        if self.is_scene_index(index, reject_dummys=False):

            return id_object.value()

        elif self.is_property_index(index):

            return id_object.fbx_object_id()

        else:
            return None

    def get_property_id(self, index):
        """Use IdObject to retrieve unique id.

        Index can be either proxy index or source index.
        """

        id_object = index.internalPointer()

        if self.is_scene_index(index, reject_dummys=False):

            raise bfQtCore.BfQtError(
                "Cannot get property id from scene index"
            )

        elif self.is_property_index(index):

            return id_object.value()

        else:
            return None

    def get_property_model(self, index):
        """stuff"""

        fbx_object_id = self.get_fbx_object_id(index)

        return self.scene_model().get_property_model(
            fbx_object_id
        )

    def get_proxy_from_object_id(self, fbx_object_id):
        row = self._fbx_object_id_to_row_map[fbx_object_id]
        return self._index_list[row]

    def mapFromSource(self, source_index):
        """
        if source_index belongs to scene model, then return super

        else if source index belongs to a property_model, then
        get object_id to find corresponding property mappings

        TODO checks

        """
        if not source_index.isValid():
            return Qt.QtCore.QModelIndex()
#             raise bfCore.BFbxError("Cannot map invalid index from source")
#             return Qt.QtCore.QModelIndex()

        if self.is_scene_index(source_index, reject_dummys=False):

            source_path = bpQtCore.IndexPath(source_index)

            if source_path.key() not in self._source_to_proxy_map:
                raise bfCore.BFbxError(
                    "Failed to map scene index from source: {}".format(
                        source_index
                    )
                )

            proxy_path = self._source_to_proxy_map[source_path.key()]

            proxy_index = proxy_path.get(self)

            return proxy_index

        elif self.is_property_index(source_index):

            property_key = self.get_property_key(source_index)
            proxy_index = self._proxy_property_indices[property_key]

            return proxy_index

        else:
            raise bfCore.BFbxError(
                "Failed to map from source: {}".format(source_index)
            )

#             return Qt.QtCore.QModelIndex()

    def mapToSource(self, proxy_index):
        """
        TODO
        """

        if not proxy_index.isValid():
            return Qt.QtCore.QModelIndex()
#             raise bfCore.BFbxError("Cannot map invalid index to source")

        if self.is_scene_index(proxy_index, reject_dummys=False):

            proxy_path = bpQtCore.IndexPath(proxy_index)

            if proxy_path.key() not in self._proxy_to_source_map:
                raise bfCore.BFbxError(
                    "Failed to map scene index to source: {}".format(
                        proxy_index
                    )
                )

            source_path = self._proxy_to_source_map[proxy_path.key()]

            source_index = source_path.get(self.sourceModel())

            return source_index

        elif self.is_property_index(proxy_index):

            property_key = self.get_property_key(proxy_index)

            if property_key not in self._proxy_to_source_property_map:
                return Qt.QtCore.QModelIndex()

            source_path = self._proxy_to_source_property_map[property_key]

            # find source index from property model
            property_model = self.get_property_model(proxy_index)
            source_index = source_path.get(property_model)

            return source_index

        else:
            raise bfCore.BFbxError(
                "Failed to map to source: {}".format(proxy_index)
            )

    def get_property_key(self, index):

        if not self.is_property_index(index):
            raise bfCore.BFbxError(
                "Cannot create key for non-property index: {}".format(index)
            )

        id_object = index.internalPointer()

        key = "{}_{}".format(
            id_object.fbx_object_id(),
            id_object.value()
        )

        return key

    def create_property_mapping(
        self, source_property_index, proxy_property_index
    ):
        """
        """
        property_key = self.get_property_key(source_property_index)

        source_path = bpQtCore.IndexPath(source_property_index)

        self._proxy_property_indices[property_key] = proxy_property_index

        self._proxy_to_source_property_map[property_key] = source_path

    def insert_source_property_index_children(
        self, source_property_model, source_property_index
    ):
        """Recursively add child property proxies to the mapping.
        """

        for row in range(source_property_model.rowCount(source_property_index)):

            child_property_index = source_property_model.index(
                row, 0, source_property_index
            )

            proxy_property_index = self.createIndex(
                row,
                0,
                child_property_index.internalPointer(),
            )

            self.create_property_mapping(
                child_property_index, proxy_property_index
            )

            self.insert_source_property_index_children(
                source_property_model, child_property_index
            )

    def create_mapping(self, source_object_index, proxy_object_index):
        """Override method to create mappings for property indices.
        """

        # create object mapping
        source_path = bpQtCore.IndexPath(source_object_index)
        proxy_path = bpQtCore.IndexPath(proxy_object_index)

        self._proxy_to_source_map[proxy_path.key()] = source_path
        self._source_to_proxy_map[source_path.key()] = proxy_path

        # don't create property mappings for dummy objects
        if self.scene_model().is_dummy(source_object_index):
            return

        # add fbx_object id mappings
        fbx_object_id = self.get_fbx_object_id(source_object_index)

#         source_path = bpQtCore.IndexPath(source_object_index)

#         self._fbx_object_id_to_proxy_map[fbx_object_id] = proxy_object_index
#         self._fbx_object_id_to_source_map[fbx_object_id] = source_path

        # TODO add this to scenelistproxymodel
        self._fbx_object_id_to_row_map[
            fbx_object_id
        ] = proxy_object_index.row()

        # add fbx_property mappings
        source_property_model = self.get_property_model(
            source_object_index
        )

        self.insert_source_property_index_children(
            source_property_model,
            # by passing in empty index we are prompting mapping to
            # start from property model root
            Qt.QtCore.QModelIndex()
        )

    def insert_source_index_children(self, source_index):
        """Recursively add children proxies to the list.
        """
        for row in range(self.sourceModel().rowCount(source_index)):

            child_index = self.sourceModel().index(row, 0, source_index)

            proxy_index = self.createIndex(
                len(self._index_list),
                0,
                child_index.internalPointer(),
            )

            self._index_list.append(proxy_index)

            self.create_mapping(child_index, proxy_index)

            self.insert_source_index_children(child_index)

    def cache_model(self):
        """Recursively get indexes from source model.
        Store in list and create mappings

        TODO connect to source model signals if neccessary.

        """

        print "Caching model: {}".format(self)

        self.beginResetModel()

        self.clear_mappings()

        # start with an invalid index to query root
        current_index = Qt.QtCore.QModelIndex()

        self.insert_source_index_children(current_index)

        self.endResetModel()

    def sourceModel(self):
        res = super(BFbxScenePropertiesProxyModel, self).sourceModel()
        return res

    def setSourceModel(self, source_model):
        """
        TODO connect all property models to cache_model()
        """

        res = super(
            BFbxScenePropertiesProxyModel, self
        ).setSourceModel(source_model)

        self.cache_model()

        source_model.dataChanged.connect(self.cache_model)
        source_model.modelReset.connect(self.cache_model)

        self.debug_properties()

        return res

    def debug_properties(self):
        print "proxy_property_indices", self._proxy_property_indices
        print "proxy_to_source_property_map", self._proxy_to_source_property_map

    def clear_mappings(self):
        """
        TODO clear property model mappings

        ** WIP **

        """
        self._source_to_proxy_map = {}
        self._proxy_to_source_map = {}
        self._index_list = []

        self._proxy_property_indices = {}
        self._proxy_to_source_property_map = {}
#         self._source_to_proxy_property_map = {}

    def parent(self, proxy_index):
        """TODO

        Check if index belongs to scene model, if it does return invalid index
        to indicate root level

        If index belongs to a property model, and source index is invalid,
        then get corresponding scene model index, or if the source index is valid then
        get the property index parent.

        Then return corresponding proxy index.


        """

        if not proxy_index.isValid():
            raise Exception("Cannot get parent of invalid index")

        if self.is_scene_index(proxy_index, reject_dummys=False):
            # scene objects have no parent
            return Qt.QtCore.QModelIndex()

        # find property index parent

        # get data from index
        fbx_object_id = self.get_fbx_object_id(proxy_index)

        property_model = self.get_property_model(proxy_index)

        property_id = self.get_property_id(proxy_index)

        property_item = property_model.get_property_item(property_id)

        property_item_parent = property_item.parent()

        if property_item_parent.is_root():

            object_proxy_index = self.get_proxy_from_object_id(
                fbx_object_id
            )

            return object_proxy_index

        else:
            # get property key from item
            # assuming it's structured in the same way
            # TODO get_property_key should use item to keep consistent
            parent_property_key = property_item_parent.key()
            return self._proxy_property_indices[parent_property_key]

    def rowCount(self, parent_index):
        """
        TODO

        if parent_index belongs to scene model, the get parent object,
        then get property model for object and return property model root row count.

        else if parent_index belongs to property model, then return
        property row count for source index.

        """
        # if at root level behaviour is normal

        # if at child level then get property data
        property_model = self.get_property_model(parent_index)

        if self.is_scene_index(parent_index, reject_dummys=True):

            return property_model.rowCount(
                Qt.QtCore.QModelIndex()
            )

        elif self.is_scene_index(parent_index, reject_dummys=False):

            # Dummy objects should display no properties
            return 0

        elif self.is_property_index(parent_index):

            if not parent_index.isValid():
                raise Exception(
                    "Cannot get property row count for invalid index: {}".format(
                        parent_index
                    )
                )

            source_parent_index = self.mapToSource(parent_index)

            row_count = property_model.rowCount(source_parent_index)
            print "debug rowCount: {}".format(row_count)
            return row_count

        elif not parent_index.isValid():

            #             print "debug getting scene rowCount: {} {}".format(
            #                 parent_index, parent_index.internalPointer()
            #             )

            row_count = len(self._index_list)

#             print "debug rowCount: {}".format(row_count)

            return row_count

        else:
            raise bfQtCore.BfQtError("Failed to get row count")

    def columnCount(self, index):
        """Lets just use the names for now
        """
        return 1

    def index(self, row, column, parent_index):
        """
        if at root level behaviour is normal

        if at child level then get property index...

        get fbx_object id, then get corresponding property mapping dict

        Then construct a bpCore.IndexPath for parent_index and append row,
        then use this to find proxy index.

        """

        if not parent_index.isValid():
            print "debugging: getting child index: {} {} {} {}".format(
                row, column, parent_index.internalPointer(), parent_index
            )

            return self._index_list[row]

        # find proxy index
        source_parent_index = self.mapToSource(parent_index)

        property_model = self.get_property_model(parent_index)

        if self.is_scene_index(source_parent_index, reject_dummys=True):

            source_property_index = property_model.index(
                row, column, Qt.QtCore.QModelIndex()
            )

        elif self.is_scene_index(source_parent_index, reject_dummys=False):

            raise bfQtCore.BfQtError(
                "Cannot create child property index of Dummy object index: {}".format(
                    parent_index
                )
            )

        elif self.is_property_index(source_parent_index):

            source_property_index = property_model.index(
                row, column, source_parent_index
            )

        else:
            raise bfQtCore.BfQtError(
                "Failed to find child property source index: {}".format(
                    parent_index
                )
            )

        return self.mapFromSource(source_property_index)

    def data(self, proxy_index, role):
        """Override data to fetch from appropriate model
        """

        if not proxy_index.isValid():
            return None

        if self.is_scene_index(proxy_index, reject_dummys=False):

            return super(BFbxScenePropertiesProxyModel, self).data(
                proxy_index, role
            )

        elif self.is_property_index(proxy_index):

            source_index = self.mapToSource(proxy_index)

            property_model = self.get_property_model(proxy_index)

            return property_model.data(source_index, role)

        else:
            return None

    def setData(self, proxy_index, role):
        """TODO?"""
        return False

    def flags(self, index):
        """ hard-coded item flags TODO """

        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        """Override to return property headers"""
        return bfPropertyModels.BFbxPropertyModel.header_data(
            section, orientation, role
        )
