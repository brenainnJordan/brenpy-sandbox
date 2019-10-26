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

    def index_path(self):
        """Return path to this node from root via indices
        """
        index_path = []

        node = self

        while node._parent is not None:
            index_path.append(
                node.index()
            )

            node = node.parent()

        index_path.reverse()

        print index_path

        return index_path

    def name(self):
        return self._name

    def name_path(self):
        name_path = []

        node = self

        while node._parent is not None:
            name_path.append(
                node.name()
            )

            node = node.parent()

        name_path.reverse()

        return name_path

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
            "object", "type", "visibility", "focalLength", "pixmap", "icon"
        ]

        self._resources = {
            "Camera": ":/out_camera.png",
            "Transform": ":/out_locator.png",
            "Joint": ":/out_joint.png",
        }

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

    def get_index_from_row_path(self, row_path, column):

        # walk hierarchy from the root node
        # until we get node at end of path
        node = self._root_node

        for row in row_path:
            node = node.child(row)

        # create index
        index = self.createIndex(row_path[-1], column, node)
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
        return 6

    def get_node_pixmap(self, node):
        if node.type() in self._resources.keys():
            resource = self._resources[node.type()]
        else:
            resource = ":/dot.png"

        pixmap = QtGui.QPixmap(resource)

        return pixmap

    def get_node_icon(self, node):
        icon = QtGui.QIcon(
            self.get_node_pixmap(node)
        )

        return icon

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
            elif column == 4:
                return self.get_node_pixmap(node)
            elif column == 5:
                return self.get_node_icon(node)
            else:
                return "null"

        elif role == QtCore.Qt.DecorationRole:
            if column == 0:
                return self.get_node_icon(node)

        # sort and filter by type instead of name
        elif role == SceneGraphModel.kSortRole:
            return node.name()

        elif role == SceneGraphModel.kFilterRole:
            return node.name()

        elif role == QtCore.Qt.BackgroundRole:
            pass
        elif role == QtCore.Qt.ForegroundRole:
            pass
        elif role == QtCore.Qt.UserRole:
            pass
        else:
            pass
#             print role


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

#     def flags(self, index):
#         """ hard-coded item flags """
# return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |
# QtCore.Qt.ItemIsEditable

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

    # drag/drop methods

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return ['text']

    def mimeData(self, indexes):
        """WIP"""
        print "mimeData()", indexes
        mimedata = QtCore.QMimeData()
#         mimedata.setData('text/xml', 'mimeData')
        node = indexes[0].internalPointer()
        index_path = [str(i) for i in node.index_path()]

        text = "nodePath:{}".format(
            ";".join(index_path)
        )

        mimedata.setText(text)
        print "mime text: ", text

        return mimedata


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
        print index.row(), index.column()

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


class TestLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        return QtGui.QLabel.__init__(self, *args, **kwargs)

    def setPixmap(self, value):
        print "PIXMAP TEST"
        return QtGui.QLabel.setPixmap(self, value)

    def setText(self, value):
        print "TEXT TEST"
        return QtGui.QLabel.setText(self, value)


class TreeToListProxyModel(QtGui.QAbstractProxyModel):
    """
    ** WIP **
    https://wiki.qt.io/Proxy_model_example_code

    TODO: switch to filter so we can use regex/wildcards etc.

    """

    def __init__(self):
        QtGui.QAbstractProxyModel.__init__(self)

        self._source_to_index_map = {}  # QtCore.Qt.QMap()
        self._index_to_source_map = {}  # QtCore.Qt.QMap()

        self._index_list = []  # QtCore.Qt.QList()

    def index(self, row, column, parent_index):
        if parent_index.isValid():
            return QtCore.QModelIndex()

        return self._index_list[row]

    def columnCount(self, parent):
        return 1

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return len(self._index_list)  # .count()

    def mapFromSource(self, source_index):
        if not source_index.isValid():
            return QtCore.QModelIndex()

        if source_index not in self._source_to_index_map:
            return QtCore.QModelIndex()

        return self._source_to_index_map[source_index]

    def mapToSource(self, proxy_index):
        if not proxy_index.isValid():
            return QtCore.QModelIndex()

        if proxy_index not in self._index_to_source_map:
            return QtCore.QModelIndex()

        return self._index_to_source_map[proxy_index]

#     def mapSelectionFromSource(const QItemSelection & sourceSelection)
#     def mapSelectionToSource(const QItemSelection & proxySelection) const

    def setSourceModel(self, source_model):
        res = QtGui.QAbstractProxyModel.setSourceModel(self, source_model)

        self.cache_model()

        source_model.dataChanged.connect(self.cache_model)

        return res

    def sourceModel(self):
        res = QtGui.QAbstractProxyModel.sourceModel(self)
        return res

    def insert_source_index_children(self, source_index):
        """Recursively add children proxies to the list.
        """
        for row in range(self.sourceModel().rowCount(source_index)):
            child_index = self.sourceModel().index(row, 0, source_index)

            proxy_index = self.createIndex(
                child_index.row(),
                child_index.column(),
                child_index.internalPointer(),
            )

            self._index_list.append(proxy_index)

            child_index = QtCore.QPersistentModelIndex(child_index)

#             self._index_map.insert(
#                 proxy_index,
#                 QtCore.QPersistentModelIndex(child_index)
#             )

            self._index_to_source_map[proxy_index] = child_index
            self._source_to_index_map[child_index] = proxy_index

            self.insert_source_index_children(child_index)

    def cache_model(self):
        """Recursively get indexes from source model.
        Store in list and create mappings

        TODO connect to source model signals if neccessary.

        """
#         self._index_list.clear()
#         self._source_parent_map.clear()
#         self._index_map.clear()

        self._source_to_index_map = {}  # QtCore.Qt.QMap()
        self._index_to_source_map = {}  # QtCore.Qt.QMap()
        self._index_list = []  # QtCore.Qt.QList()

        # start with an invalid index to query root
        current_index = QtCore.QModelIndex()

        self.insert_source_index_children(current_index)


class CustomCompleter(QtGui.QCompleter):
    def __init__(self):
        return QtGui.QCompleter.__init__(self)

    def splitPath(self, path):
        return path.split(".")

    def pathFromIndex(self, index):
        node = index.internalPointer()
        path_list = node.name_path()
        path_str = ".".join(path_list)
        return path_str

#         return QtCore.Qt.QString(path_str)


class IconMapperWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(IconMapperWidget, self).__init__(parent)

        self.lyt = QtGui.QHBoxLayout()

        self.pixmap_label = TestLabel()
        self.name_label = TestLabel()

        # create completer
#         self.completer = QtGui.QCompleter()
        self.completer = CustomCompleter()
#         completer->setModelSorting(QCompleter::CaseInsensitivelySortedModel);

        self.completer.setCompletionMode(
            QtGui.QCompleter.PopupCompletion
            #             QtGui.QCompleter.UnfilteredPopupCompletion
        )

        self.completer_tree_view = QtGui.QTreeView()

        self.completer.setPopup(self.completer_tree_view)

        # completer line edit
        self.edit_widget = QtGui.QLineEdit()
        self.edit_widget.setCompleter(self.completer)

        # regular widgets for testing drag and drop
        self.edit_widget2 = QtGui.QLineEdit()

        self.combo = QtGui.QComboBox()

        self.test_btn = QtGui.QPushButton()

        self.pixmap_label.setFixedWidth(20)
        self.name_label.setFixedWidth(100)
        self.test_btn.setFixedWidth(100)

        self.lyt.addWidget(self.pixmap_label)
        self.lyt.addWidget(self.name_label)
        self.lyt.addWidget(self.edit_widget)
        self.lyt.addWidget(self.edit_widget2)
        self.lyt.addWidget(self.test_btn)
        self.lyt.addWidget(self.combo)

        self.setLayout(self.lyt)

    def configure_completer_tree(self):
        self.completer_tree_view.setRootIsDecorated(True)
        self.completer_tree_view.header().hide()
        self.completer_tree_view.header().setStretchLastSection(False)

        self.completer_tree_view.header().setResizeMode(
            0, QtGui.QHeaderView.Stretch
        )

        self.completer_tree_view.header().setResizeMode(
            1, QtGui.QHeaderView.ResizeToContents
        )

        for i in range(1, self.completer_tree_view.header().count()):
            self.completer_tree_view.hideColumn(i)

        self.completer_tree_view.expandAll()

    # if using a regular model
    def setModel(self, model):
        self.model = model

        if True:
            # test
            # we can set btn icon like this and text will map correctly
            # but we can't bind icon and text at same time
            resource = self.model._resources["Camera"]
            pixmap = QtGui.QPixmap(resource)
            icon = QtGui.QIcon(pixmap)
            self.test_btn.setIcon(icon)

        # create widget mapping
        self.data_mapper = QtGui.QDataWidgetMapper()
        self.data_mapper.setModel(self.model)

        # set completer

        self.list_model = TreeToListProxyModel()
        self.list_model.setSourceModel(self.model)

        self.completer.setModel(self.list_model)
        self.configure_completer_tree()

        # mapping(widget, column)
#         self.data_mapper.addMapping(self.edit_widget, 0)
        self.data_mapper.addMapping(self.edit_widget2, 0)
# self.data_mapper.addMapping(self.label_widget, 0, "text") # overrides
# pixmap

        self.data_mapper.addMapping(self.pixmap_label, 4, "pixmap")
        self.data_mapper.addMapping(self.name_label, 0, "text")

        # can't do both!?
        self.data_mapper.addMapping(self.test_btn, 0, "text")
#         self.data_mapper.addMapping(self.test_btn, 5, "icon")

        self.data_mapper.addMapping(self.combo, 0)

#         self.data_mapper.addMapping(self.type_widget.edit, 1)

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


class NodeDropMenu(QtGui.QMenu):

    def __init__(self, parent):
        QtGui.QMenu.__init__(self, parent)
        self.create_actions()

    def create_actions(self):
        self.clear_action = self.addAction('Clear')
        self.select_action = self.addAction('Select')

    def perform_action(self, action):
        """redundant"""
        #         action = self.exec_(self.mapToGlobal(position))

        if action == self._clear_action:
            pass
        elif action == self._select_action:
            pass


class NodeDropWidget(QtGui.QWidget):
    """Widget that accepts node drag/drop.
    mime data contains path to node via rows serialized as a string.
    """

    def __init__(self, parent=None):
        super(NodeDropWidget, self).__init__(parent)

        self._mapped = False

        self.setAcceptDrops(True)
        self.setMouseTracking(False)

        self.setToolTip("drag a thing on to me!")

        self.data_mapper = QtGui.QDataWidgetMapper()

        self.setFixedHeight(50)

        self._create_widgets()
        self._create_layout()
        self._define_context_menu()

        self.accept_palette = QtGui.QPalette()

        self.accept_palette.setColor(
            QtGui.QPalette.Background, QtCore.Qt.green
        )

        self.frame_widget.setAutoFillBackground(True)

    def _define_context_menu(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self._context_menu = NodeDropMenu(self)

        if True:
            # python style connect
            self.customContextMenuRequested.connect(
                self._show_context_menu
            )

            self._context_menu.clear_action.triggered.connect(
                self.clear
            )

            self._context_menu.select_action.triggered.connect(
                self.select_node
            )

        else:
            # cpp style connect
            QtCore.QObject.connect(
                self,
                QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"),
                # QtCore.SIGNAL("customContextMenuRequested(QPoint)"), # also
                # works
                self._show_context_menu
            )

            QtCore.QObject.connect(
                self._context_menu.clear_action,
                QtCore.SIGNAL("triggered()"),
                # QtCore.SIGNAL("customContextMenuRequested(QPoint)"), # also
                # works
                self.clear
            )

    def _show_context_menu(self, point):
        self._context_menu.exec_(
            self.mapToGlobal(point)
        )

    def _create_widgets(self):

        self.node_label = QtGui.QLabel("node drop:")

        self.frame_widget = QtGui.QFrame()

        self.frame_widget.setFrameStyle(
            QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken
            #             QtGui.QFrame.Panel | QtGui.QFrame.Raised
        )

        self.frame_widget.setLineWidth(1)
#         self.frame_widget.setMidLineWidth(1)
#         self.frame_widget.setContentsMargins(1, 1, 1, 1)

        self.pixmap_label = QtGui.QLabel()
        self.name_label = QtGui.QLabel("test")

        self.node_label.setFixedWidth(100)

        self.pixmap_label.setFixedWidth(20)
#         self.pixmap_label.setFixedHeight(15)

    def _create_layout(self):
        self.lyt = QtGui.QHBoxLayout()
        self.frame_lyt = QtGui.QHBoxLayout()
        self.frame_lyt.setContentsMargins(5, 0, 5, 0)

        self.lyt.addWidget(self.node_label)
        self.frame_lyt.addWidget(self.pixmap_label)
        self.frame_lyt.addWidget(self.name_label)
        self.lyt.addWidget(self.frame_widget)

        self.setLayout(self.lyt)
        self.frame_widget.setLayout(self.frame_lyt)

    def set_accept_color(self):
        #         m_myWidget->setPalette(pal);
        self.frame_widget.setPalette(
            self.accept_palette
        )

    def reset_color(self):
        self.frame_widget.setPalette(
            self.palette()
        )

    def dragEnterEvent(self, e):

        data = e.mimeData()

        if data.hasText():

            text = data.text()

            if text.startswith("nodePath:"):
                e.accept()
                self.set_accept_color()
            else:
                e.ignore()
                self.reset_color()

        else:
            e.ignore()

    def dropEvent(self, e):

        self.reset_color()

        data = e.mimeData()
        text = data.text()
        path_str = text[len("nodePath:"):]

        path = path_str.split(";")
        index_path = [int(i) for i in path]
        print "index path: {}".format(index_path)

        qt_index = self.model.get_index_from_row_path(index_path, 0)

        print "name: ", qt_index.internalPointer().name()

        if not self._mapped:
            self.add_mappings()

        self.data_mapper.setRootIndex(qt_index.parent())
        self.data_mapper.setCurrentModelIndex(qt_index)

    def dragLeaveEvent(self, event):
        self.reset_color()
        return QtGui.QWidget.dragLeaveEvent(self, event)

    def setModel(self, model):
        self.model = model

        self.data_mapper.setModel(self.model)
#         self.map_to_index()

    def add_mappings(self):
        self.data_mapper.addMapping(self.pixmap_label, 4, "pixmap")
        self.data_mapper.addMapping(self.name_label, 0, "text")
        self._mapped = True
#         self.data_mapper.toFirst()

    def setSelection(self, index, old_index):
        if not self._mapped:
            self.add_mappings()

        self.data_mapper.setRootIndex(index.parent())
        self.data_mapper.setCurrentModelIndex(index)

    def select_node(self):
        print "select node"

    def clear(self):
        self.data_mapper.clearMapping()
        self._mapped = False
        self.name_label.setText("- none -")
        self.pixmap_label.setPixmap(None)

    def underMouse(self, *args, **kwargs):
        print "poop"
        return QtGui.QWidget.underMouse(self, *args, **kwargs)

    def mouseMoveEvent(self, e):
        #
        #         if e.buttons() != QtCore.Qt.MidButton:
        #             return

        frame_pos = self.frame_widget.mapFrom(self, e.pos())

        if self.frame_widget.rect().contains(frame_pos):
            print True
        else:
            print False
#         drag.setHotSpot(e.pos() - self.rect().topLeft())


class NodeLabelWidget(QtGui.QWidget):
    """Stuff"""

    def __init__(self, parent=None):
        super(NodeLabelWidget, self).__init__(parent)

        self._mapped = False

        self.data_mapper = QtGui.QDataWidgetMapper()

        self.setFixedHeight(50)

        self._create_widgets()
        self._create_layout()

    def _create_widgets(self):
        self.pixmap_label = QtGui.QLabel()
        self.text_label = QtGui.QLabel()
        self.pixmap_label.setFixedWidth(20)
#         self.pixmap_label.setFixedHeight(15)

    def _create_layout(self):
        self.lyt = QtGui.QHBoxLayout()
        self.lyt.addWidget(self.pixmap_label)
        self.lyt.addWidget(self.text_label)
        self.setLayout(self.lyt)

    def setModel(self, model):
        self.model = model

        self.data_mapper.setModel(self.model)
#         self.map_to_index()

    def add_mappings(self):
        self.data_mapper.addMapping(self.pixmap_label, 4, "pixmap")
        self.data_mapper.addMapping(self.text_label, 0, "text")
        self._mapped = True
#         self.data_mapper.toFirst()

    def setSelection(self, index):
        if not self._mapped:
            self.add_mappings()

        self.data_mapper.setRootIndex(index.parent())
        self.data_mapper.setCurrentModelIndex(index)

    def clear(self):
        self.data_mapper.clearMapping()
        self._mapped = False
        self.name_label.setText("")
        self.pixmap_label.setPixmap(None)

    def get_node(self):
        parent_index = self.data_mapper.rootIndex()
        row = self.data_mapper.currentIndex()
        index = self.model.index(row, 0, parent_index)
        node = index.internalPointer()
        return node


class NodeCompleterWidget(QtGui.QWidget):
    """
    TODO highlight current index in tree.
    """

    def __init__(self, parent=None):
        super(NodeCompleterWidget, self).__init__(parent)

        self._current_index = QtCore.QModelIndex()

        self.lyt = QtGui.QHBoxLayout()

        self.label = QtGui.QLabel("nodeCompleterWidget")

        # create completer
#         self.completer = QtGui.QCompleter()
        self.completer = CustomCompleter()
#         completer->setModelSorting(QCompleter::CaseInsensitivelySortedModel);

        self.completer.setCompletionMode(
            QtGui.QCompleter.PopupCompletion
            #             QtGui.QCompleter.UnfilteredPopupCompletion
        )

        # completer line edit
        self.edit_widget = QtGui.QLineEdit()
        self.edit_widget.setCompleter(self.completer)

        # mapped label widget
        self.node_label_widget = NodeLabelWidget()

        self.lyt.addWidget(self.label)
        self.lyt.addWidget(self.edit_widget)
        self.lyt.addWidget(self.node_label_widget)

        self.setLayout(self.lyt)

    def setModel(self, model):
        self.model = model

        # set completer
        self.list_model = TreeToListProxyModel()
        self.list_model.setSourceModel(self.model)

        self.completer.setModel(self.list_model)

        self.node_label_widget.setModel(self.model)

        self.connect_widgets()

    def set_current_index(self, index):
        self._current_index = index
        self.node_label_widget.setSelection(index)

    def completer_activated(self, completer_index):

        proxy_index = self.completer.completionModel().mapToSource(completer_index)

        index = self.list_model.mapToSource(proxy_index)

        self.set_current_index(index)

        print self.get_node().name()

    def connect_widgets(self):
        #         self.completer.activated.connect(self.print_test, QtCore.QModelIndex)
        QtCore.QObject.connect(
            self.completer,
            QtCore.SIGNAL("activated(QModelIndex)"),
            self.completer_activated
        )

    def set_node(self, node):
        index_path = node.index_path()
        index = self.model.get_index_from_row_path(index_path, 0)

        self.set_current_index(index)

    def get_node(self):
        #         return self.node_label_widget.get_node()
        node = self._current_index.internalPointer()
        return node


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
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

#         self.list_view = QtGui.QListView()
        self.icon_map_test = IconMapperWidget()

        self.node_drop_widget = NodeDropWidget()

        self.node_completer_widget = NodeCompleterWidget()

        # add to layout
        self.lyt.addWidget(self.filter_box)
        self.lyt.addWidget(self.check_box)
        self.lyt.addWidget(self.tree)
        self.lyt.addWidget(self.inspector_widget)
        self.lyt.addWidget(self.icon_map_test)
        self.lyt.addWidget(self.node_drop_widget)
        self.lyt.addWidget(self.node_completer_widget)

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

            self.icon_map_test.setProxyModel(self.proxy_model)

            self.node_drop_widget.setModel(self.model)

            self.node_completer_widget.setModel(self.model)

            # connect inspector widget to tree selection
            QtCore.QObject.connect(
                self.tree.selectionModel(),
                QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                self.inspector_widget.setProxySelection
            )

            QtCore.QObject.connect(
                self.tree.selectionModel(),
                QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                self.icon_map_test.setProxySelection
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

#         # connect list view
#         self.list_model = QtGui.QSortFilterProxyModel()
#         self.list_model.setSourceModel(self.model)
# #         self.list_model.setSortRole(SceneGraphModel.kSortRole)
#         self.list_model.setFilterRole(SceneGraphModel.kFilterRole)
#         self.list_model.setFilterWildcard("blah")
#
#         self.list_view.setModel(self.list_model)

        # test adding a new node
        new_node = Node("test")
        self.model.addNode(new_node, joint)

        print root.log()

        self.tree.expandAll()

        # test setting completer widget
        self.node_completer_widget.set_node(new_node)

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
