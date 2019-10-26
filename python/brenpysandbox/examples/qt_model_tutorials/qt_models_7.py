'''
Created on 9 Jun 2018

Proxy models, filtering and sorting

https://www.youtube.com/watch?v=KWhHwOG0ZO8

'''

from PySide import QtCore, QtGui

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
            parent.addChild(self)

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

    def addingChild(self):
        return self._adding_child

    def child(self, index):
        return self._children[index]

    def children(self):
        return self._children

    def addChild(self, child, index=None):
        self.beginAddingChild()

        if child._parent is not None:
            child._parent.remove_child()
        elif child not in self._children:
            if index is not None:
                self._children.insert(index, child)
            else:
                self._children.append(child)

            child._parent = self

        self.endAddingChild()

    def insertChild(self, index, child):
        self.addChild(child, index=index)

    def removeChild(self, child):
        if child not in self._children:
            return

        self._children.remove(child)
        child._parent(None)

    def popChild(self, index):
        child = self._children.pop(index)
        child._parent(None)

    def childCount(self, recursive=False):
        child_count = len(self._children)

        if recursive:
            for child in self._children:
                child_count += child.childCount(recursive=True)

        return child_count

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
        if isinstance(parent, Node):
            parent.addChild(self)
        elif parent is None:
            self._parent.removeChild(self)
        else:
            raise TypeError(
                "Parent must be of type(Node) or None, not type({})".format(type(parent)))

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
            ** Overide Method **

            Create QModelIndex representing desired model item.

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

    def getNode(self, index):
        """ Convenience method
            * redundant? *
        """

        if not index.isValid():
            return self._root_node

        node = index.internalPointer()
        if node is None:
            pass

        return node

    def rowCount(self, index):
        if not index.isValid():
            node = self._root_node
        else:
            node = index.internalPointer()

        return node.childCount()

    def columnCount(self, index=None):
        return 3

    def data(self, index, role):
        """
            ** overide method **

            Called by view to get data for specified QModelIndex for specified role
        """

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
                    resource = resources[node.type()]
                    pixmap = QtGui.QPixmap(resource)
                    icon = QtGui.QIcon(pixmap)
                    return icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
            ** overide method **

            Called with EditRole by view when user enters text into specified QModelIndex

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

    def insertColumn(self, *args, **kwargs):
        raise NotImplementedError("Use addNode or createNode instead")

    def insertColumns(self, *args, **kwargs):
        raise NotImplementedError("Use addNodes or createNodes instead")

    def insertRow(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNode instead")

    def insertRows(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNodes instead")

    def addNode(self, node, parent):
        parent.addChild(node)

        self.dataChanged.emit(
            QtCore.QModelIndex(),
            self.createIndex(self._root_node.childCount(recursive=True), 0)
        )


class Gui(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self._create_widgets()
        self._populate()

    def _create_widgets(self):
        self.lyt = QtGui.QVBoxLayout(self)
        self.filter_box = QtGui.QLineEdit()
        self.check_box = QtGui.QCheckBox("enable sorting")
        # self.check_box.setChecked(True)

        self.tree = QtGui.QTreeView()
        self.lyt.addWidget(self.filter_box)
        self.lyt.addWidget(self.check_box)
        self.lyt.addWidget(self.tree)

    def _populate(self):
        root = Node("root")
        group = Transform("group", root)
        cube = Node("cube", group)
        camera = Camera("camera", root)
        joint = Joint("poop_joint", group)
        root_joint = Joint("root_joint", root)
        hips_joint = Joint("hips_joint", root_joint)

        print root.log()

        self.model = SceneGraphModel(root)

        self.proxy_model = QtGui.QSortFilterProxyModel()

        # OR
        # subclass QtGui.QAbstractProxyModel

        self.proxy_model.setSourceModel(self.model)

        # connect text changed signal of lineEdit to setFilterRegExp method
        # passing QString as arg
        QtCore.QObject.connect(
            self.filter_box,
            QtCore.SIGNAL("textChanged(QString)"),
            # self.proxy_model.setFilterRegExp
            self.proxy_model.setFilterWildcard
        )

        QtCore.QObject.connect(
            self.check_box,
            QtCore.SIGNAL("stateChanged(int)"),
            self.tree.setSortingEnabled
        )

        # self.tree.setModel(self.model)
        self.tree.setModel(self.proxy_model)
        # self.tree.setSortingEnabled(True)

        new_node = Node("test")
        self.model.addNode(new_node, joint)

        print root.log()


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    gui = Gui()
    gui.show()

    sys.exit(app.exec_())
