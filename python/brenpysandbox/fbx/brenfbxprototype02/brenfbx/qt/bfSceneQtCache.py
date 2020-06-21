'''Classes to cache data between fbx scene and qt models.

Because fbx class instances as volitile, we need to avoid as much
direct communication between qt objects and the fbx scene
wherever reasonable.

For example fbx objects that return other fbx objects (eg. getChild)
might not always return the same object, or might not register
as the same object with Qt and potentially cause null pointer issues.

To get around this we create a temporary store of any fbx object or property
that we want to interact with via Qt.

To gain access to the objects via the cache we do so by using a unique ID
for the object or property we are looking for.

The QtModelIndex internal pointers look to instances of the BfIdData class,
instead of to the fbx objects or properties directly.

This also helps to ensure any broken pointers between objects.

In the case of fbx properties, these do not have native unique Ids,
so we create our own custom hierarchy, with our own unique id management.

/* (depricated)
The custom property hierarchy also allows us to customise in interesting ways,
such as listing property components such as xyz values as children.
*/

'''

import os
import fbx

from brenfbx.core import bfIO
from brenfbx.utils import bfFbxUtils
from brenfbx.core import bfCore

# from brenrig.sandbox import fbx_prototype_01

from brenfbx.qt import bfPropertyQtCache
from brenfbx.qt import bfQtCore


class BfIdData(object):
    def __init__(self, init_value=0):
        super(BfIdData, self).__init__()

        self._value = init_value

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class BfIdDummyData(object):
    def __init__(self, init_value=0):
        super(BfIdDummyData, self).__init__()

        self._value = init_value

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class BfIdConData(BfIdData):
    """For connection models
    """

    def __init__(self, init_value=0):
        super(BfIdConData, self).__init__()

        self._value = init_value


class BFbxSceneCache(object):
    def __init__(self, fbx_scene, fbx_manager):
        """
        pass
        """
        super(BFbxSceneCache, self).__init__()

        self._scene = fbx_scene
        self._fbx_manager = fbx_manager
        self.root_node = fbx_scene.GetRootNode()

        # id data of all objects connected to the scene
        self.id_data = {}
        self.id_list = []

        # id objects allow for safe Qt pointers
        self.id_objects = {}

        # dummy objects allow for FbxNodes to appear "twice" in a model.
        # the dummy would appear under the scene connections
        # and the "real" item appears under the parent
        # (if it has a parent)
        self.id_dummy_objects = {}

        # property caches
        self.property_caches = {}

        # object connection id objects
        self.id_con_objects = {}

        # cache all objects under the scene
        self.add_object(self._scene)
        self.cache_connected(self._scene)

    def add_object(self, fbx_object):
        """Add FbxObject or FbxNode to cache
        """

        if not isinstance(fbx_object, (fbx.FbxObject)):
            raise bfCore.BfError(
                "Cannot add object to cache, must be instance of FbxObject or subclass. ({})".format(
                    fbx_object
                )
            )

        # get unique id
        object_id = fbx_object.GetUniqueID()

        # check if this object is already cached
        if object_id in self.id_data:
            raise bfCore.BfError(
                "Object already cached: {}".format(fbx_object.GetName())
            )

        # append id data
        self.id_data[object_id] = fbx_object
        self.id_list.append(object_id)

        # create BfIdData object
        id_object = BfIdData(object_id)
        self.id_objects[object_id] = id_object

        # create dummy object
        dummy_object = BfIdDummyData(object_id)
        self.id_dummy_objects[object_id] = dummy_object

        # create property cache
        property_cache = bfPropertyQtCache.BFbxPropertyCache(fbx_object)
        self.property_caches[object_id] = property_cache

        # create connection id object
        id_con_object = BfIdConData(object_id)
        self.id_con_objects[object_id] = id_con_object

        return True

    def remove_object(self, fbx_object):
        """Remove FbxObject or FbxNode to cache
        """
        if not isinstance(fbx_object, (fbx.FbxObject)):
            raise bfCore.BfError(
                "object to remove must be instance of FbxObject or subclass. ({})".format(
                    fbx_object
                )
            )

        # get unique id
        object_id = fbx_object.GetUniqueID()

        # check if this object is in the cached
        if object_id not in self.id_data:
            raise bfCore.BfError(
                "Object not cached, cannot remove: {}".format(
                    fbx_object.GetName())
            )

        # destroy property cache
        property_cache = self.property_caches.pop(object_id)

        # destroy dummy object
        dummy_object = self.id_dummy_objects.pop(object_id)
#         del dummy_object

        # destroy BfIdData object
        bf_id_object = self.id_objects.pop(object_id)
#         del bf_id_object

        # destroy id and cache
        fbx_object = self.id_data.pop(object_id)
#         self.id_list.pop(object_id)
        self.id_list.remove(object_id)

        return True

    def create_object(self, fbx_cls, name=None):
        """Create fbx object and add to cache

        TODO use class id object instead?
        ie FbxClassId.Create(...)

        TODO create property cache for new object

        """

        # check user input
        if not issubclass(fbx_cls, fbx.FbxObject):
            raise bfCore.BfError(
                "Fbx class must be subclass of FbxObject: {}".format(
                    fbx_cls
                )
            )

        # validate name
        if name is None:
            name = str(fbx_cls.__name__)

        name = bfFbxUtils.get_unique_name(name, self._scene)

        # create object
        fbx_object = fbx_cls.Create(self._fbx_manager, name)

        # connect object to scene
        self._scene.ConnectSrcObject(fbx_object)

        # add object to cache
        self.add_object(fbx_object)

        return fbx_object

    def delete_object(self, fbx_object):
        """Safely destroy FbxObject
        """
        self.remove_object(fbx_object)
        fbx_object.Destroy()
        return True

    def delete_object_by_id(self, object_id):
        """Safely find and destroy FbxObject using unique ID
        """
        fbx_object = self.get_object(object_id)
        self.delete_object(fbx_object)
        return True

    def cache_connected(self, fbx_object):
        """Add objects connected as source to cache.
        """
        for i in range(fbx_object.GetSrcObjectCount()):
            src_object = fbx_object.GetSrcObject(i)

            self.add_object(src_object)

    def get_object(self, object_id):
        """Get cached FbxObject for specified uid
        """

        if isinstance(object_id, (BfIdData, BfIdDummyData)):
            object_id = object_id.value()

        if object_id not in self.id_data:
            raise bfCore.BfError(
                "No id found: {}".format(object_id)
            )
#             return None

        return self.id_data[object_id]

    def get_id_object(self, object_id):
        """Get cached BfIdData object for specified uid
        """
        if object_id not in self.id_objects:
            raise bfQtCore.BfQtError(
                "Failed to get id object: {} {}".format(
                    object_id
                )
            )

        return self.id_objects[object_id]

    def get_id_dummy_object(self, object_id):
        """Get cached BfIdDummyData object for specified uid
        """
        if object_id not in self.id_dummy_objects:
            raise bfQtCore.BfQtError(
                "Failed to get id dummy object: {} {}".format(
                    object_id
                )
            )

        return self.id_dummy_objects[object_id]

    def get_id_con_object(self, object_id):
        """Get cached BfIdConData object for specified uid
        """
        if object_id not in self.id_con_objects:
            raise bfQtCore.BfQtError(
                "Failed to get id con object: {} {}".format(
                    object_id
                )
            )

        return self.id_con_objects[object_id]

    def get_property_cache(self, object_id):
        """Get cached BFbxPropertyCache for specified uid
        """
        if object_id not in self.property_caches:
            return None

        return self.property_caches[object_id]

    def print_debug_info(self):
        print "Scene objects:"
        for uid in self.id_list:
            fbx_object = self.id_data[uid]
            print "\t", uid, fbx_object.GetName(), fbx_object


def test(fbx_file):
    fbx_scene, fbx_manager = bfIO.load_fbx_file(
        fbx_file,
        fbx_manager=None,
        settings=None,
        verbose=True,
        err=True
    )

    cache = BFbxSceneCache(fbx_scene, fbx_manager)
    cache.print_debug_info()


if __name__ == "__main__":
    DUMP_DIR = r"D:\Repos\dataDump\brenrig"
    TEST_FILE = "fbx_property_hierarchy_test_01.fbx"
    TEST_PATH = os.path.join(DUMP_DIR, TEST_FILE)

    test(TEST_PATH)
