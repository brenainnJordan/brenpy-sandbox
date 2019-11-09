'''
Created on 9 Jun 2018

Tree view and hierarchies

to convert icons to qt binary .py file
C:\Python27\Lib\site-packages\PySide>pyside-rcc
E:\dev\python\standalone_tools\examples\qt_model_tutorials\icons\icons.xml
-o E:\dev\python\standalone_tools\examples\qt_model_tutorials\icons\icons.py

'''

try:
    from Qt import QtCore, QtWidgets, QtGui
except ImportError:
    print "[ WARNING ] Cannot find Qt library, using PySide2 instead"
    from PySide2 import QtCore, QtWidgets, QtGui

from icons import icons
import sys

# icons.qt_resource_data


class Root(object):
    def __init__(self):
        self._children = []

    def child(self, index):
        return self._children[index]

    def add_child(self, child):
        if child in self._children:
            return
        elif child.parent() is not None:
            child.parent.remove_child()

        self._children.append(child)

    def remove_child(self, child):
        if child not in self._children:
            return

        self._children.remove(child)

    def child_count(self):
        return len(self._children)


class Node(object):
    def __init__(self, name, parent=None):
        #super(Node, self).__init__()

        self._children = []
        self._parent = None
        self._name = None
        self._adding_child = False  # redundant?

        self.setName(name)

        if parent is not None:
            parent.add_child(self)

    def type(self):
        return self.__class__.__name__

    def beginAddingChild(self):
        """
            :TODO safety thing, if a re-parenting goes wrong, we can return to previous state
            kinda like a transaction
            Also to help avoid getting into infinite recursions
        """
        self._adding_child = True

    def endAddingChild(self):
        self._adding_child = False

    def child(self, index):
        return self._children[index]

    def children(self):
        return self._children

    def add_child(self, child):
        self.beginAddingChild()

        if child._parent is not None:
            child._parent.remove_child()
        elif child not in self._children:
            self._children.append(child)
            child._parent = self

        self.endAddingChild()

    def remove_child(self, child):
        if child not in self._children:
            return

        self._children.remove(child)

    def child_count(self):
        return len(self._children)

    def index(self):
        if self._parent is None:
            return None

        return self._parent._children.index(self)

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def parent(self):
        return self._parent

    def setParent(self, parent):
        parent.add_child(self)

    def log(self, level=-1):

        level += 1

        output = "{}|-{}\n".format("    " * level, self.name())

        for child in self._children:
            output += child.log(level)

        return output


class Transform(Node):
    def __init__(self, name, parent=None):
        super(Transform, self).__init__(name, parent)


class Camera(Node):
    def __init__(self, name, parent=None):
        super(Camera, self).__init__(name, parent)


class Joint(Node):
    def __init__(self, name, parent=None):
        super(Joint, self).__init__(name, parent)


class SceneGraphModel(QtCore.QAbstractItemModel):
    def __init__(self, root_node, parent=None):
        super(SceneGraphModel, self).__init__(parent)

        self._root_node = root_node
        self._horizontal_headers = ["object", "type"]

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        #row = index.row()
        #column = index.column()

        # get the node stored in this index
        node = index.internalPointer()
        parent_node = node.parent()

        if parent_node == self._root_node:
            # return empty index to indicate it has no parent and avoid errors
            return QtCore.QModelIndex()

        # create a new index with pointer to our parent node
        # (row, column, object to point to)
        parent_index = self.createIndex(parent_node.index(), 0, parent_node)

        return parent_index

    def index(self, row, column, parent_index):
        """
            The term "index" in this case is not used as the index of a list such as an integer
            "index" refers to a QModelIndex class instance, which contains a pointer to our data.
            The data in this case is a Node class instance.

            http://doc.qt.io/qt-5/qabstractitemmodel.html#createIndex

            I guess a QModelIndex is a more portable/abstract represenation of this model instance

            :TODO find out when this is called?
        """

        if not parent_index.isValid():  # ie. if parent() returned an empty QModelIndex() and there is no parent
            parent_node = self._root_node
        else:
            parent_node = parent_index.internalPointer()

        node = parent_node.child(row)

        if not node:  # i mean why not?
            return QtCore.QModelIndex()  # return empty index

        # create new index with pointer to desired Node
        index = self.createIndex(row, column, node)
        return index

    def rowCount(self, index):
        if not index.isValid():
            node = self._root_node
        else:
            node = index.internalPointer()

        return node.child_count()

    def columnCount(self, index):
        return 3

    def data(self, index, role):
        if not index.isValid():
            return

        row = index.row()
        column = index.column()
        node = index.internalPointer()

        if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:

            if column == 0:
                return node.name()
            elif column == 1:
                return node.type()
            else:
                return "null"

        if role == QtCore.Qt.DecorationRole:
            resources = {
                "Camera": ":/out_camera.png",
                "Transform": ":/out_locator.png",
                "Joint": ":/out_joint.png",
            }

            if column == 0:
                if node.type() in resources.keys():
                    pixmap = QtGui.QPixmap(resources[node.type()])
                    icon = QtGui.QIcon(pixmap)
                    return icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        :param index QModelIndex
        :param value QVariant
        :param role int (QtCore.Qt namespace enum)
        """

        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            node = index.internalPointer()
            node.setName(value)

            self.dataChanged.emit(index, index)

            return True

        return False

    def flags(self, index):
        """ hard-coded item flags """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < len(self._horizontal_headers):
                    return self._horizontal_headers[section]
                else:
                    return "other"

    """
    :TODO continue tutorial from getNode()
    """


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    root = Node("root")
    group = Transform("group", root)
    cube = Node("cube", group)
    camera = Camera("camera", root)
    joint = Joint("poop_joint", group)

    print root.log()

    model = SceneGraphModel(root)

    tree = QtWidgets.QTreeView()
    tree.setModel(model)
    tree.show()

    tree1 = QtWidgets.QTreeView()
    tree1.setModel(model)
    tree1.show()

    sys.exit(app.exec_())
