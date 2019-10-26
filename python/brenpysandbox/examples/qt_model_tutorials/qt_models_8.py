'''
Created on 9 Jun 2018

Proxy models, custom userRole filtering/sorting
Mapped widgets
Static properties

https://www.youtube.com/watch?v=x1Emco2SXWY
https://www.youtube.com/watch?v=7omei2RCtDI
https://www.youtube.com/watch?v=Gil-dg3ajbA

:notes
In the tutorial he deals with showing different types of properties for different nodes
by hiding and showing widgets with hard-coded property widgets with lots of if statements,
and manually mapping data types with widgets.
This seems a bit clunky, so we've skipped that for now.

But in summary he adds the extra data as extra columns, eg pos xyz or focal length, for ALL nodes, regardless of type
Kind of like a database, and the node subclasses dictate if those columns can be set etc.

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
        self._visibility = True

    def setVisibility(self, visibility):
        if not isinstance(visibility, bool):
            return False

        self._visibility = visibility

    def isVisibile(self):
        return self._visibility


class Camera(Node):
    def __init__(self, name, parent=None):
        super(Camera, self).__init__(name, parent)
        self._focal_length = 18.0

    def setFocalLength(self, focal_length):
        if not isinstance(focal_length, (int, float)):
            return False

        self._focal_length = focal_length

        return True

    def focalLength(self):
        return self._focal_length


class Joint(Transform):
    def __init__(self, name, parent=None):
        super(Joint, self).__init__(name, parent)


class SceneGraphModel(QtCore.QAbstractItemModel):

    # define custom role enums for returning specific data to sort by
    kSortRole = QtCore.Qt.UserRole
    kFilterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root_node, parent=None):
        super(SceneGraphModel, self).__init__(parent)

        self._root_node = root_node
        self._horizontal_headers = [
            "object", "type", "visibility", "focalLength"]

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
        return 4

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
            elif column == 2 and isinstance(node, Transform):
                return node.isVisibile()
            elif column == 3 and isinstance(node, Camera):
                return node.focalLength()
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

        # sort and filter by type instead of name
        if role == SceneGraphModel.kSortRole:
            return node.name()

        if role == SceneGraphModel.kFilterRole:
            return node.name()

#         # sort and filter by type instead of name
#         if role == SceneGraphModel.kSortRole:
#             return node.type()
#
#         if role == SceneGraphModel.kFilterRole:
#             return node.type()

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

        row = index.row()
        column = index.column()
        node = index.internalPointer()

        if role == QtCore.Qt.EditRole:
            if column == 0:
                node.setName(value)
            elif column == 2 and isinstance(node, Transform):
                node.setVisibility(value)
            elif column == 3 and isinstance(node, Camera):
                node.setFocalLength(value)

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


class LabeledLineEditWidget(QtGui.QWidget):
    def __init__(self, label, parent=None):
        super(LabeledLineEditWidget, self).__init__(parent)

        self.lyt = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel(label)
        self.edit = QtGui.QLineEdit()

        self.label.setMinimumWidth(50)

        self.lyt.addWidget(self.label)
        self.lyt.addWidget(self.edit)

        self.setLayout(self.lyt)


class InspectorWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(InspectorWidget, self).__init__(parent)

        self.lyt = QtGui.QVBoxLayout()

        # hard code a couple of property widgets
        self.name_widget = LabeledLineEditWidget("name")
        self.type_widget = LabeledLineEditWidget("type")

        self.lyt.addWidget(self.name_widget)
        self.lyt.addWidget(self.type_widget)

        self.setLayout(self.lyt)

    # if using a regular model
    def setModel(self, model):
        self.model = model

        # create widget mapping
        self.data_mapper = QtGui.QDataWidgetMapper()
        self.data_mapper.setModel(self.model)

        # mapping(widget, column)
        self.data_mapper.addMapping(self.name_widget.edit, 0)
        self.data_mapper.addMapping(self.type_widget.edit, 1)

        # bind mapper to first row in model
        self.data_mapper.toFirst()

    def setSelection(self, index, old_index):
        self.data_mapper.setRootIndex(index.parent())
        self.data_mapper.setCurrentModelIndex(index)

    # if using a proxy model for sorting/filtering etc
    def setProxyModel(self, proxy_model):
        self._proxy_model = proxy_model
        self.setModel(proxy_model.sourceModel())

    def setProxySelection(self, proxy_index, old_proxy_index):
        index = self._proxy_model.mapToSource(proxy_index)
        old_index = self._proxy_model.mapToSource(old_proxy_index)
        self.setSelection(index, old_index)


class HierarchySortFitler(QtGui.QSortFilterProxyModel):
    """Allows parents of filtered row to remain visible.

    https://stackoverflow.com/questions/250890/using-qsortfilterproxymodel-with-a-tree-model
    """

    def filterAcceptsRow(self, source_row, source_parent):
        # custom behaviour
        if not self.filterRegExp().isEmpty():

            # get source model index for current row
            source_index = self.sourceModel().index(
                source_row, self.filterKeyColumn(), source_parent)

            if source_index.isValid():
                # if any of children matches the filter, then current index
                # matches the filter as well

                row_count = self.sourceModel().rowCount(source_index)

                for i in range(row_count):
                    if self.filterAcceptsRow(i, source_index):
                        return True

                # check current index itself :
                key = self.sourceModel().data(source_index, self.filterRole())

                # TODO shouldn't this use regex?
#                 return self.filterRegExp().exactMatch(key)
#                 print self.filterRegExp().pattern()
                return self.filterRegExp().pattern() in key

        # parent call for initial behaviour
        return QtGui.QSortFilterProxyModel.filterAcceptsRow(self, source_row, source_parent)


class Gui(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        self._create_widgets()
        self._populate()

    def _create_widgets(self):
        self.lyt = QtGui.QVBoxLayout(self)
        self.filter_box = QtGui.QLineEdit()
        self.check_box = QtGui.QCheckBox("enable sorting")
        self.check_box.setChecked(True)

        self.inspector_widget = InspectorWidget()

        self.tree = QtGui.QTreeView()

        # add to layout
        self.lyt.addWidget(self.filter_box)
        self.lyt.addWidget(self.check_box)
        self.lyt.addWidget(self.tree)
        self.lyt.addWidget(self.inspector_widget)

    def _populate(self):
        root = Node("root")
        group = Transform("group", root)
        cube = Node("cube", group)
        camera = Camera("camera", root)
        joint = Joint("poop_joint", group)
        root_joint = Joint("root_joint", root)
        hips_joint = Joint("hips_joint", root_joint)

        parent = hips_joint

        for i in range(20):
            parent = Joint("blah{}".format(i), parent)

        print root.log()

        self.model = SceneGraphModel(root)

        if True:  # using filtering etc.
            #             self.proxy_model = QtGui.QSortFilterProxyModel()

            # custom sort filter
            self.proxy_model = HierarchySortFitler()

            # set filter options
            self.proxy_model.setFilterCaseSensitivity(
                QtCore.Qt.CaseSensitivity.CaseInsensitive)

            # OR
            # subclass QtGui.QAbstractProxyModel

            self.proxy_model.setSourceModel(self.model)

            # set our custom role enum to be called when sending sortRole to
            # things
            self.proxy_model.setSortRole(SceneGraphModel.kSortRole)
            self.proxy_model.setFilterRole(SceneGraphModel.kFilterRole)

            # connect text changed signal of lineEdit to setFilterRegExp method
            # passing QString as arg
#             QtCore.QObject.connect(
#                 self.filter_box,
#                 QtCore.SIGNAL("textChanged(QString)"),
#                 # self.proxy_model.setFilterRegExp
#                 self.proxy_model.setFilterWildcard
#             )

            self.filter_box.textChanged.connect(self._filter_edit_changed)

            QtCore.QObject.connect(
                self.check_box,
                QtCore.SIGNAL("stateChanged(int)"),
                self.tree.setSortingEnabled
            )

            # self.tree.setModel(self.model)
            self.tree.setModel(self.proxy_model)
            self.tree.setSortingEnabled(True)
            self.tree.setSelectionMode(
                QtGui.QAbstractItemView.ExtendedSelection
            )

            self.inspector_widget.setProxyModel(self.proxy_model)

            # connect inspector widget to tree selection
            QtCore.QObject.connect(
                self.tree.selectionModel(),
                QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                self.inspector_widget.setProxySelection
            )

        else:
            self.tree.setModel(self.model)
            self.inspector_widget.setModel(self.model)

            # connect inspector widget to tree selection
            QtCore.QObject.connect(
                self.tree.selectionModel(),
                QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                self.inspector_widget.setSelection
            )

        # test adding a new node
        new_node = Node("test")
        self.model.addNode(new_node, joint)

        print root.log()

        self.tree.expandAll()

    def _filter_edit_changed(self):
        #         self.model._filtered_nodes = []
        #         self.proxy_model._highlighted_indices = []
        self.proxy_model.setFilterWildcard(self.filter_box.text())
        self.tree.expandAll()


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    gui = Gui()
    gui.show()

    sys.exit(app.exec_())
