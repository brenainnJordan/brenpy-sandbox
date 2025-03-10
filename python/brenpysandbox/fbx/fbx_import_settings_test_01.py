import fbx

import sys

import brenfbx.utils.fbx_utils.bfFbxPropertyUtils

try:
    from Qt import QtCore
    from Qt import QtWidgets
    from Qt import QtGui
except ImportError:
    print "[ WARNING ] Cannot find Qt library, using PySide2 instead"
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtGui

# QtCore.SIGNAL doesn't seem to exist
# TODO investigate why
try:
    from PySide.QtCore import SIGNAL
except ImportError:
    from PySide2.QtCore import SIGNAL

from brenfbx.qt.property import bfQtPropertyTreeWidgets
from brenfbx.items import bfPropertyItems
from brenfbx.qt.property import bfQtPropertyModels

def inspect_child_properties(fbx_property, indent=0):
    """Recursively debug properties
    """

    child_property = fbx_property.GetChild()

    while child_property.IsValid():
        print "-"*indent, child_property.GetName()
        inspect_child_properties(child_property, indent=indent+1)

        child_property = child_property.GetSibling()


def test_1():

    fbx_manager = fbx.FbxManager.Create()

    settings = fbx.FbxIOSettings.Create(
        fbx_manager, fbx.IOSROOT
    )

    print settings

    root_properties = brenfbx.utils.fbx_utils.bfFbxPropertyUtils.get_root_properties(settings)

    for property in root_properties:
        print property.GetName()
        inspect_child_properties(property, indent=1)

    # fbx_property = settings.GetFirstProperty()
    #
    # while fbx_property.IsValid():
    #     print fbx_property.GetName()
    #
    #     fbx_property = settings.GetNextProperty(fbx_property)

class Test2(object):
    def __init__(self):
        self.fbx_manager = fbx.FbxManager.Create()

        self.settings = fbx.FbxIOSettings.Create(
            self.fbx_manager, fbx.IOSROOT
        )

        item_manager = bfPropertyItems.BfFbxPropertyTreeItemManager(self.fbx_manager)
        item_manager.set_debug_level(item_manager.LEVELS.mid)

        item_manager.set_fbx_object(self.settings)

        model = bfQtPropertyModels.BfFbxPropertyModel()
        model.set_item_manager(item_manager)

        import_property = self.settings.FindProperty("Import")
        print import_property, import_property.IsValid()
        model.set_root_fbx_property(import_property)

        # self._properties_widget = bfQtPropertyWidgets.BfPropertiesWidget(self.fbx_manager)
        self._properties_widget = bfQtPropertyTreeWidgets.BfPropertyTreeWidget()
        self._properties_widget.set_property_model(model)

        # self._properties_widget.set_fbx_object(self.settings)

        # for child_property in bfUtils.get_child_properties(import_property):
        #     print child_property.GetName()

        self._properties_widget.show()

if __name__ == "__main__":
    # test_1()
    # TODO use bf environment

    app = QtWidgets.QApplication(sys.argv)

    test = Test2()

    sys.exit(app.exec_())
