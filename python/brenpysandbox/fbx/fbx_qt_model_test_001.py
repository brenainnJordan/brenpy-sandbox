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

import sys

import fbx

try:
    import Qt
except ImportError:
    import PySide2 as Qt

try:
    from PySide.QtCore import SIGNAL
except ImportError:
    from PySide2.QtCore import SIGNAL

# import icon resources into memory
from icons import icons

# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_fbx_ascii_test_001.fbx"
TEST_FILE = r"C:\Users\Bren\Desktop\tests\rig_to_test_002.fbx"

ATTRIBUTE_ENUM_LABELS = {
    fbx.FbxNodeAttribute.eUnknown: "unidentified",
    fbx.FbxNodeAttribute.eNull: "null",
    fbx.FbxNodeAttribute.eMarker: "marker",
    fbx.FbxNodeAttribute.eSkeleton: "skeleton",
    fbx.FbxNodeAttribute.eMesh: "mesh",
    fbx.FbxNodeAttribute.eNurbs: "nurbs",
    fbx.FbxNodeAttribute.ePatch: "patch",
    fbx.FbxNodeAttribute.eCamera: "camera",
    fbx.FbxNodeAttribute.eCameraStereo: "stereo",
    fbx.FbxNodeAttribute.eCameraSwitcher: "camera switcher",
    fbx.FbxNodeAttribute.eLight: "light",
    fbx.FbxNodeAttribute.eOpticalReference: "optical reference",
    fbx.FbxNodeAttribute.eOpticalMarker: "marker",
    fbx.FbxNodeAttribute.eNurbsCurve: "nurbs curve",
    fbx.FbxNodeAttribute.eTrimNurbsSurface: "trim nurbs surface",
    fbx.FbxNodeAttribute.eBoundary: "boundary",
    fbx.FbxNodeAttribute.eNurbsSurface: "nurbs surface",
    fbx.FbxNodeAttribute.eShape: "shape",
    fbx.FbxNodeAttribute.eLODGroup: "lodgroup",
    fbx.FbxNodeAttribute.eSubDiv: "subdiv",
}

# key: fbx.FbxNodeAttribute.EType, value: str ref to compiled Qt icon resource
ATTRIBUTE_ENUM_ICONS = {
    #     fbx.FbxNodeAttribute.eUnknown: "unidentified",
    fbx.FbxNodeAttribute.eNull: ":/out_locator.png",  # i guess?
    #     fbx.FbxNodeAttribute.eMarker: "marker",
    fbx.FbxNodeAttribute.eSkeleton: ":/out_joint.png",
    #     fbx.FbxNodeAttribute.eMesh: "mesh",
    #     fbx.FbxNodeAttribute.eNurbs: "nurbs",
    #     fbx.FbxNodeAttribute.ePatch: "patch",
    fbx.FbxNodeAttribute.eCamera: ":/out_camera.png",
    fbx.FbxNodeAttribute.eCameraStereo: ":/out_camera.png",  # TODO
    fbx.FbxNodeAttribute.eCameraSwitcher: ":/out_camera.png",  # TODO
    #     fbx.FbxNodeAttribute.eLight: "light",
    #     fbx.FbxNodeAttribute.eOpticalReference: "optical reference",
    #     fbx.FbxNodeAttribute.eOpticalMarker: "marker",
    #     fbx.FbxNodeAttribute.eNurbsCurve: "nurbs curve",
    #     fbx.FbxNodeAttribute.eTrimNurbsSurface: "trim nurbs surface",
    #     fbx.FbxNodeAttribute.eBoundary: "boundary",
    #     fbx.FbxNodeAttribute.eNurbsSurface: "nurbs surface",
    #     fbx.FbxNodeAttribute.eShape: "shape",
    #     fbx.FbxNodeAttribute.eLODGroup: "lodgroup",
    #     fbx.FbxNodeAttribute.eSubDiv: "subdiv",
}

ICON_DIR = r"D:/Repos/brenpy/brenpy/sandbox/fbx/icons"

QTREEVIEW_STYLE_SHEET = """
QTreeView::branch:has-siblings:!adjoins-item {{
    border-image: url({dir}/stylesheet-vline.png) 0;
}}

QTreeView::branch:has-siblings:adjoins-item {{
    border-image: url({dir}/stylesheet-branch-more.png) 0;
}}

QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
    border-image: url({dir}/stylesheet-branch-end.png) 0;
}}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {{
        border-image: none;
        image: url({dir}/stylesheet-branch-closed.png);
}}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings  {{
        border-image: none;
        image: url({dir}/stylesheet-branch-open.png);
}}
""".format(dir=ICON_DIR)


def get_fbx_node_index(fbx_node):
    """Find node in parent and return index.
    """
    parent = fbx_node.GetParent()

    for i in range(parent.GetChildCount()):
        if parent.GetChild(i) is fbx_node:
            return i

    # if we get to this point, somethings gone wrong!
    raise Exception("Failed to find parent: {0}".format(fbx_node.GetName()))


def get_fbx_node_attribute_label(fbx_node):
    """Return convinient name for fbx node attribute."""

    fbx_attribute = fbx_node.GetNodeAttribute()
    enum_id = fbx_attribute.GetAttributeType()

    if not enum_id in ATTRIBUTE_ENUM_LABELS:
        return ""
    else:
        return ATTRIBUTE_ENUM_LABELS[enum_id]


def get_fbx_node_attribute_icon(fbx_node):
    """Return suitable icon for fbx node attribute."""

    fbx_attribute = fbx_node.GetNodeAttribute()
    enum_id = fbx_attribute.GetAttributeType()

    if not enum_id in ATTRIBUTE_ENUM_ICONS:
        return None
    else:
        return ATTRIBUTE_ENUM_ICONS[enum_id]


class FbxSceneQtModel(Qt.QtCore.QAbstractItemModel):

    # define custom role enums for returning specific data to sort by
    kSortRole = Qt.QtCore.Qt.UserRole
    kFilterRole = Qt.QtCore.Qt.UserRole + 1

    def __init__(self, fbx_scene, parent=None):
        super(FbxSceneQtModel, self).__init__(parent)

        # TODO be careful for empty pointer if the scene is deleted
        self._fbx_scene = fbx_scene
        self._root_node = self._fbx_scene.GetRootNode()

        # temp way of holding references to FbxNodes to stop them being destroyed
        # TODO find better solution
        self._nodes = set([])

#         self._filtered_nodes = ["Hips"]

        self._horizontal_headers = [
            "object", "type", "visibility"
        ]

    def parent(self, index):
        if not index.isValid():
            return Qt.QtCore.QModelIndex()

        #row = index.row()
        #column = index.column()

        # get the node stored in this index
        node = index.internalPointer()
        parent_node = node.GetParent()

        if parent_node == self._root_node:
            # return empty index to indicate it has no parent and avoid errors
            return Qt.QtCore.QModelIndex()

        # create a new index with pointer to our parent node
        # (row, column, object to point to)
        parent_index = self.createIndex(
            get_fbx_node_index(parent_node), 0, parent_node
        )

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
            # for now return root node
            # TODO we also want to iterate through connections to non-transform
            # nodes
            parent_node = self._root_node
        else:
            parent_node = parent_index.internalPointer()

        node = parent_node.GetChild(row)

        if not node:  # i mean why not?
            return Qt.QtCore.QModelIndex()  # return empty index

        # temp way of holding references to FbxNodes to stop them being destroyed
        # TODO find better solution

        # using a list seemed to get progressivly slower
        # set seems happy, keep testing
#         if node not in self._nodes:
#             self._nodes.append(node)

        self._nodes.add(node)

        # create new index with pointer to desired Node
        index = self.createIndex(row, column, node)

        return index

    def rowCount(self, index):
        if not index.isValid():
            node = self._root_node
        else:
            node = index.internalPointer()

        return node.GetChildCount()

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
        name = node.GetName()

        if role in [Qt.QtCore.Qt.DisplayRole, Qt.QtCore.Qt.EditRole]:

            if column == 0:
                return name
            elif column == 1:
                return get_fbx_node_attribute_label(node)
            elif column == 2 and isinstance(node, fbx.FbxNode):
                return node.GetVisibility()
            else:
                return "null"

        if role == Qt.QtCore.Qt.DecorationRole:

            if column == 0:
                icon_file = get_fbx_node_attribute_icon(node)

                if icon_file is not None:
                    pixmap = Qt.QtGui.QPixmap(icon_file)
                    icon = Qt.QtGui.QIcon(pixmap)
                    return icon

        # sort/filter by name
        if role == FbxSceneQtModel.kSortRole:
            return name

        if role == FbxSceneQtModel.kFilterRole:
            return name

#         # sort and filter by type instead of name
#         if role == FbxSceneQtModel.kSortRole:
#             return get_fbx_node_attribute_label(node)
#
#         if role == FbxSceneQtModel.kFilterRole:
#             return get_fbx_node_attribute_label(node)

        # highlight color etc.
#         if role == Qt.QtCore.Qt.BackgroundRole:
#             if node.GetName() in self._filtered_nodes:
#                 print node.GetName()
#                 return Qt.QtWidgets.QColor(255, 255, 0)

    def setData(self, index, value, role=Qt.QtCore.Qt.EditRole):
        """
            ** overide method **

            Called with EditRole by view when user enters text into specified QModelIndex

            :param index QModelIndex
            :param value QVariant
            :param role int (Qt.QtCore.Qt namespace enum)

        """

        if not index.isValid():
            return False

        row = index.row()
        column = index.column()
        node = index.internalPointer()

        if role == Qt.QtCore.Qt.EditRole:
            if column == 0:
                node.SetName(value)
            elif column == 2 and isinstance(node, fbx.FbxNode):
                node.SetVisibility(value)
            elif column == 3 and isinstance(node, fbx.FbxCamera):
                #                 node.setFocalLength(value)
                pass

            self.dataChanged.emit(index, index)

            return True

        return False

    def flags(self, index):
        """ hard-coded item flags """
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable | Qt.QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):

        if role == Qt.QtCore.Qt.DisplayRole:
            if orientation == Qt.QtCore.Qt.Horizontal:
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

#     def addNode(self, node, parent):
#         parent.addChild(node)
#
#         self.dataChanged.emit(
#             Qt.QtCore.QModelIndex(),
#             self.createIndex(self._root_node.childCount(recursive=True), 0)
#         )


class LabeledLineEditWidget(Qt.QtWidgets.QWidget):
    def __init__(self, label, parent=None):
        super(LabeledLineEditWidget, self).__init__(parent)

        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.label = Qt.QtWidgets.QLabel(label)
        self.edit = Qt.QtWidgets.QLineEdit()

        self.label.setMinimumWidth(50)

        self.lyt.addWidget(self.label)
        self.lyt.addWidget(self.edit)

        self.setLayout(self.lyt)


class InspectorWidget(Qt.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InspectorWidget, self).__init__(parent)

        self.lyt = Qt.QtWidgets.QVBoxLayout()

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
        self.data_mapper = Qt.QtWidgets.QDataWidgetMapper()
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


class HierarchySortFitler(Qt.QtCore.QSortFilterProxyModel):
    """Allows parents of filtered row to remain visible.

    https://stackoverflow.com/questions/250890/using-qsortfilterproxymodel-with-a-tree-model

    TODO tidy up
    """

    def __init__(self, *args, **kwargs):
        super(HierarchySortFitler, self).__init__(*args, **kwargs)
        self._highlighted_indices = set([])
#         self._highlighted_nodes = []
        self._old_filter_wildcard = ""

    def data(self, index, role):
        """
            ** overide method **

            Called by view to get data for specified QModelIndex for specified role
        """

#         row = index.row()
#         column = index.column()

        if not index.isValid():
            return

        if role == Qt.QtCore.Qt.BackgroundRole:
            # TODO use uniqueID instead of name??

            #             GetUniqueID
            #             node = index.internalPointer()
            #             print node
            #             name = self.sourceModel().data(index, Qt.QtCore.Qt.DisplayRole)
            #             print name
            name = Qt.QtCore.QSortFilterProxyModel.data(
                self, index, Qt.QtCore.Qt.DisplayRole
            )

            if name in self._highlighted_indices:
                return Qt.QtGui.QColor(255, 255, 0)
#             if node.GetName() in self._filtered_nodes:
#                 print node.GetName()
#                 return Qt.QtWidgets.QColor(255, 255, 0)
        else:
            return Qt.QtCore.QSortFilterProxyModel.data(self, index, role)

#     def setFilterWildcard(self, pattern, *args, **kwargs):
#         #         if pattern != self._old_filter_wildcard:
#         #             self._highlighted_indices = []
#         #             self._old_filter_wildcard = pattern
#
# return Qt.QtWidgets.QSortFilterProxyModel.setFilterWildcard(self, pattern,
# *args, **kwargs)

    def filterAcceptsRow(self, source_row, source_parent):
        # custom behaviour
        if not self.filterRegExp().isEmpty():

            #             model = self.sourceModel()

            # get source model index for current row
            source_index = self.sourceModel().index(
                source_row, self.filterKeyColumn(), source_parent)

            if source_index.isValid():

                # check current index
                key = self.sourceModel().data(source_index, self.filterRole())
                match = self.filterRegExp().exactMatch(key)

                if match:
                    name = self.sourceModel().data(source_index, Qt.QtCore.Qt.DisplayRole)
                    self._highlighted_indices.add(name)

                # if any of children matches the filter, then current index
                # matches the filter as well

                row_count = self.sourceModel().rowCount(source_index)

                for i in range(row_count):
                    if self.filterAcceptsRow(i, source_index):
                        return True

                # check current index itself :
                return match

#                 regexp = self.filterRegExp()
#                 regexp.setMinimal(False)
#                 print regexp.patternSyntax()
#                 if self.filterRegExp().exactMatch(key):
                #                     model._filtered_nodes.append(
                #                         source_index.internalPointer().GetName()
                #                     )

                #                     self._highlighted_indices.append(name)
                #                     model.setData(source_index, 1, role="poop")
#                     return True
#                 print regexp.matchedLength(), key
#                 return regexp.matchedLength() > 0
#                 print self.filterRegExp().pattern()
#                 print self.filterRegExp().caseSensitivity()
                return self.filterRegExp().pattern() in key

        # parent call for initial behaviour
        return Qt.QtCore.QSortFilterProxyModel.filterAcceptsRow(self, source_row, source_parent)


class Gui(Qt.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)

        self._filter_value = ""

        self._create_widgets()
        self._connect_widgets()

        # get test scene
        self._fbx_manager = fbx.FbxManager.Create()
        io_settings = fbx.FbxIOSettings.Create(self._fbx_manager, fbx.IOSROOT)
        self._fbx_manager.SetIOSettings(io_settings)
        fbx_importer = fbx.FbxImporter.Create(self._fbx_manager, "")

        # Use the first argument as the filename for the importer.
        try:
            fbx_importer.Initialize(
                TEST_FILE, -1, self._fbx_manager.GetIOSettings()
            )
        except Exception as err:
            msg = "Call to FbxImporter::Initialize() failed.\n"
            msg += "Error returned: {0}".format(
                fbx_importer.GetStatus().GetErrorString()
            )
            print msg
            raise err

        self._fbx_scene = fbx.FbxScene.Create(
            self._fbx_manager, "TestScene"
        )

        fbx_importer.Import(self._fbx_scene)
        fbx_importer.Destroy()

        self._populate()

    def _create_widgets(self):
        self.lyt = Qt.QtWidgets.QVBoxLayout(self)
        self.filter_box = Qt.QtWidgets.QLineEdit()
        self.check_box = Qt.QtWidgets.QCheckBox("enable sorting")
        self.check_box.setChecked(True)

        self.inspector_widget = InspectorWidget()

        self.proxy_model = HierarchySortFitler()
        self.tree = Qt.QtWidgets.QTreeView()
        self.tree.setIndentation(10)

        # add to layout
        self.lyt.addWidget(self.filter_box)
        self.lyt.addWidget(self.check_box)
        self.lyt.addWidget(self.tree)
        self.lyt.addWidget(self.inspector_widget)

    def _populate(self):

        # populate widgets
        self.model = FbxSceneQtModel(self._fbx_scene)

        if True:  # using filtering etc.
            #             self.proxy_model = Qt.QtCore.QSortFilterProxyModel()

            # custom filter

            # set filter options
            self.proxy_model.setFilterCaseSensitivity(
                Qt.QtCore.Qt.CaseSensitivity.CaseInsensitive)

            # OR
            # subclass Qt.QtWidgets.QAbstractProxyModel

            self.proxy_model.setSourceModel(self.model)

            # set our custom role enum to be called when sending sortRole to
            # things
            self.proxy_model.setSortRole(FbxSceneQtModel.kSortRole)
            self.proxy_model.setFilterRole(FbxSceneQtModel.kFilterRole)

            # connect text changed signal of lineEdit to setFilterRegExp method
            # passing QString as arg
#             Qt.QtCore.QObject.connect(
#                 self.filter_box,
#                 Qt.QtCore.SIGNAL("textChanged(QString)"),
#                 # self.proxy_model.setFilterRegExp
#                 self.proxy_model.setFilterWildcard
#             )

#             Qt.QtCore.QObject.connect(
#                 self.check_box,
#                 Qt.QtCore.SIGNAL("stateChanged(int)"),
#                 self.tree.setSortingEnabled
#             )

            # self.tree.setModel(self.model)
            self.tree.setModel(self.proxy_model)
            self.tree.setSortingEnabled(True)
            self.tree.setSelectionMode(
                Qt.QtWidgets.QAbstractItemView.ExtendedSelection
            )

            self.inspector_widget.setProxyModel(self.proxy_model)

#             connect inspector widget to tree selection
            Qt.QtCore.QObject.connect(
                self.tree.selectionModel(),
                #                 Qt.QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                self.inspector_widget.setProxySelection
            )
#             self.tree.selectionModel().currentChanged.connect(
#                 self.inspector_widget.setProxySelection
#             )
        else:
            self.tree.setModel(self.model)
            self.inspector_widget.setModel(self.model)

#             self.tree.selectionModel().currentChanged.connect(
#                 self.inspector_widget.setSelection
#             )

            # connect inspector widget to tree selection
            Qt.QtCore.QObject.connect(
                self.tree.selectionModel(),
                #                 Qt.QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
                self.inspector_widget.setSelection
            )

        self.tree.expandAll()

    def _connect_widgets(self):
        self.filter_box.textChanged.connect(self._filter_edit_changed)
        self.check_box.stateChanged.connect(self.tree.setSortingEnabled)

    def _filter_edit_changed(self):
        value = self.filter_box.text()

        if value == self._filter_value:
            return

        self._filter_value = value

        #         self.model._filtered_nodes = []
        self.proxy_model._highlighted_indices.clear()
        self.proxy_model.setFilterWildcard(value)
        self.tree.expandAll()

    def destroy(self, *args, **kwargs):
        print "test**"
        # destroy fbx objects
        self._fbx_manager.Destroy()
        del self._fbx_manager  # , fbx_scene

        return Qt.QtWidgets.QWidget.destroy(self, *args, **kwargs)

#         # test adding a new node
#         new_node = Node("test")
#         self.model.addNode(new_node, joint)
#
#         print root.log()


if __name__ == "__main__":

    app = Qt.QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet(QTREEVIEW_STYLE_SHEET)
#     app.setStyleSheet("QLineEdit { background-color: yellow }")

    gui = Gui()
    gui.show()

    sys.exit(app.exec_())
