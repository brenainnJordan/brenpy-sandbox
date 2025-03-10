"""constraint type stuff
"""
import os
import sys

from Qt import QtWidgets

import fbx
from brenfbx.utils import bfFileUtils


#
# TEST_FILE_PATH = r"D:\Repos\dataDump\fbx_tests\maya_constraints_test_003.fbx"
#
# TEST_FILE_PATH = r"D:\Repos\dataDump\brenfbx\brenfbx_test_scene_01.fbx"
#
# fbx_scene, fbx_manager = bfIO.load_file(
#     TEST_FILE_PATH,
#     fbx_manager=None,
#     settings=None,
#     verbose=True,
#     err=True
# )
#
# # find constraints and nodes
# constraints = []
#
# src_count = fbx_scene.GetSrcObjectCount()
#
# for i in range(src_count):
#     src = fbx_scene.GetSrcObject(i)
#     if isinstance(src, fbx.FbxConstraint):
#         constraints.append(src)
#
# print constraints
#
# for constraint in constraints:
#     print constraint
#     print constraint.ClassId.GetName()

#
# node2 = p_cons.GetConstrainedObject()
# node1 = p_cons.GetConstraintSource(0)
# node0 = node1.GetParent()

class Test(QtWidgets.QWidget):
    def __init__(self):
        super(Test, self).__init__()

        self._scene, self.fbx_manager = bfFileUtils.load_fbx_file(
            os.path.join(DUMP_DIR, TEST_FILE),
            fbx_manager=None,
            settings=None,
            verbose=True,
            err=True
        )

        # find constraints and nodes
        constraints = []

        src_count = self._scene.GetSrcObjectCount()

        for i in range(src_count):
            src = self._scene.GetSrcObject(i)
            if isinstance(src, fbx.FbxConstraint):
                constraints.append(src)

        print constraints

if __name__ == "__main__":

    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
#     TEST_FILE = "fbx_scene_sorting_example_01.fbx"
#     TEST_FILE = "fbx_property_hierarchy_test_01.fbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"

    app = QtWidgets.QApplication(sys.argv)

    if True:
        test = Test()
        test.show()

    sys.exit(app.exec_())
