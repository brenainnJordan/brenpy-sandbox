"""Stuff
"""

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

from brenfbx.qt import bfSceneModels, bfPropertyModels
from brenfbx.qt import bfConnectionProxyModels


class BfSceneModelManager(object):
    def __init__(self):
        self._scene_model = None
        self._property_model = None
        self._connection_model_manager = None

        self.create_scene_model()
        self.create_property_model()
        self.create_connection_model_manager()

    def create_scene_model(self):
        self._scene_model = bfSceneModels.BFbxSceneTreeQtModel()
        self._scene_filter_model = bfSceneModels.BFbxSceneDummyFilterModel()
        self._scene_filter_model.setSourceModel(self._scene_model)

    def scene_model(self):
        return self._scene_model

    def scene_filter_model(self):
        return self._scene_filter_model

    def set_scene(self, fbx_scene, fbx_manager):
        self._scene_model.set_scene(fbx_scene, fbx_manager)

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
            self._scene_model,
            parent=None
        )

        self._scene_model.add_parity_model(self._property_model)

    def property_model(self):
        return self._property_model

    def create_connection_model_manager(self):
        self._connection_model_manager = bfConnectionProxyModels.BfConnectionModelManager()

        self._connection_model_manager.set_models(
            self._scene_model, self._property_model
        )
#         self._connection_model_manager.set_scene_model(self._scene_model)

        for model in self._connection_model_manager.object_connection_models():
            self._scene_model.add_parity_model(model)

        for model in self._connection_model_manager.property_connection_models():
            self._property_model.add_parity_model(model)

    def connection_model_manager(self):
        return self._connection_model_manager
