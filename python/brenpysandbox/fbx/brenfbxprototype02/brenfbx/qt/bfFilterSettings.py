"""
TODO

Create generic (non Qt) classes to manage filter settings.

Must support serialize and deserialize.

Must manage child settings classes such as fbx types.

Must support getter methods, such as get_filtered_fbx_types()
to pass simplified data to filter models. 

Idea being we can launch a filter settings dialog with an instance
of this class, the dialog can create qt models required to edit data.

The scene widget would manage this class, maybe create a temporary
copy of the class first to pass to dialog, if accepted then copy
the data to the main class and update appropriate filter models etc.

The main fbx editor widget would manage when and where to save this data,
eg it may have it's own serialize and deserialize, that creates data about
what widgets have been created and their settings, and stores it to
a FbxStringProperty in the scene, that can be deserialized when re-opening.

When it comes to expanding this for rigging system,
this can be subclassed to add rig-specific settings,
eg. filter only guides

"""
import json
import fbx

from brenfbx.core import bfData


class BfFbxTypesFilterSettings(object):
    def __init__(self, fbx_manager=None, data=None):

        self._data_root = bfData.FbxClassIdBoolRoot(fbx_manager)
        self._models = ["list", "tree"]
        self._model_index = 0

        if data is not None:
            self.deserialize(data)

    def data_root(self):
        return self._data_root

    def models(self):
        return self._models

    def model_index(self):
        return self._model_index

    def set_model_index(self, index):
        """TODO checks"""
        self._model_index = index
        return True

    def enabled_class_ids(self):
        class_ids = []

        for item in self._data_root.find_items_by_value(True):
            class_ids.append(item.class_id())

        return class_ids

    def serialize(self, as_json=False, pretty=False):
        data = {
            "models": self._models,
            "model_index": self._model_index,
            "data_root": self._data_root.serialize(as_json=False),
        }

        if as_json:
            if pretty:
                data = json.dumps(
                    data,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            else:
                data = json.dumps(data)

        return data

    def deserialize(self, data):
        """
        TODO check keys
        TODO check models
        """
        root_data = data["data_root"]

        self._data_root.deserialize(root_data)
        self.set_model_index(data["model_index"])

        return True


class BfSceneFilterSettings(object):
    def __init__(self, fbx_manager=None, data=None):

        self._fbx_types = BfFbxTypesFilterSettings(
            fbx_manager=fbx_manager, data=None
        )

        if data is not None:
            self.deserialize(data)

    def fbx_types(self):
        return self._fbx_types

    def serialize(self, as_json=False, pretty=False):
        data = {
            "fbx_types": self._fbx_types.serialize(as_json=False)
        }

        if as_json:
            if pretty:
                data = json.dumps(
                    data,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            else:
                data = json.dumps(data)

        return data

    def deserialize(self, data):
        fbx_types_data = data["fbx_types"]

        self._fbx_types.deserialize(fbx_types_data)

        return True

    def debug(self):
        print self.serialize(as_json=True, pretty=True)


if __name__ == "__main__":
    test = BfSceneFilterSettings()
    test.debug()
