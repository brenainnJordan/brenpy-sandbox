'''Simple Qt widget to view and edit the contents of an fbx file.

TODO edit stuff

notes:

When trying to simplify the Model structure to avoid using internalPointers
and querying the hierarchy via row indices alone,
we got into some infinite loops when querying the ModelIndex parent
to get the parent row (in order to walk up the hierarchy to get all the row indices).
It seemed as though the self.parent(index) method was always expecting us
to create a new ModelIndex using row index sourced from external data.
(this would query index.parent()) 
If we created the index from an existing parent, why would this not work?
Does index.parent() simply call model.parent()???
TODO investigate further.
Also setting the parent index as internalPointer didn't work either.

Also TODO
Find out why using the node_id as an internal pointer didn't work.
Cos that's still a valid alternative for simplifying stuff.

'''

import sys
import os

import fbx
import FbxCommon

from brenfbx.core import bfData
reload(bfData)

from brenpy.utils import bpStr
reload(bpStr)

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

# import icon resources into memory
from brenpy.examples.qt_model_tutorials.icons import icons

# TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_fbx_ascii_test_001.fbx"
# TEST_FILE = r"C:\Users\Bren\Desktop\tests\rig_to_test_002.fbx"
TEST_FILE = r"C:\Users\Bren\Desktop\tests\joints_export_test_001.fbx"

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

    if not enum_id in bfData.ATTRIBUTE_ENUM_LABELS:
        return ""
    else:
        return bfData.ATTRIBUTE_ENUM_LABELS[enum_id]


def get_fbx_node_attribute_icon(fbx_node):
    """Return suitable icon for fbx node attribute."""

    fbx_attribute = fbx_node.GetNodeAttribute()
    enum_id = fbx_attribute.GetAttributeType()

    if not enum_id in ATTRIBUTE_ENUM_ICONS:
        return None
    else:
        return ATTRIBUTE_ENUM_ICONS[enum_id]


class FbxPropertyColumn(object):
    """
    Assumes that property instance being passed into methods is already
    cast as the correct property type subclass.

    ie. fbx.FbxPropertyBool1(fbx.FbxProperty).Get()

    TODO subclass per column instead of using static/class methods?
    """

    # get and set values via string using BpStr
    VIA_STR = True

    def __init__(self, name, get_method, set_method):
        self._name = name
        self._get = get_method
        self._set = set_method

    def name(self):
        return self._name

    def get(self, fbx_property):
        """Return qt friendly data from property."""
        if self._get:
            value = self._get(fbx_property)
            return value

    def set(self, fbx_property, value):
        if self._set:
            return self._set(fbx_property, value)

    @classmethod
    def get_property_name(cls, fbx_property):
        name = fbx_property.GetName()
        # GetName() returns a fbx.FbxString
        # so we should convert to str first
        return str(name)

    @classmethod
    def get_property_value(cls, fbx_property):
        value = fbx_property.Get()

        if cls.VIA_STR:
            data_cls = cls.get_bpstr_data_type(fbx_property)
            value = data_cls.to_str(value)
        else:
            # cast as qt readable object
            data_cls = cls.get_python_data_type(fbx_property)
            value = data_cls(value)

        return value

    @classmethod
    def set_property_value(cls, fbx_property, value):
        print value

        if cls.VIA_STR:
            data_cls = cls.get_bpstr_data_type(fbx_property)
            try:
                value = data_cls.from_str(value)
            except bpStr.BpStrException as err:
                print err.message
                return False

        return fbx_property.Set(value)

    @classmethod
    def get_python_data_type(cls, fbx_property):
        prop_type_enum = fbx_property.GetPropertyDataType().GetType()
        prop_type = type(prop_type_enum)

        if prop_type not in bfData.FBX_ENUM_NAMES.keys():
            # return string by default
            return str

        prop_data_dict = bfData.FBX_ENUM_NAMES[prop_type]

        if prop_type_enum not in prop_data_dict.keys():
            # return string by default
            return str

        return prop_data_dict[prop_type_enum]

    @classmethod
    def get_bpstr_data_type(cls, fbx_property):
        prop_type_enum = fbx_property.GetPropertyDataType().GetType()
        prop_type = type(prop_type_enum)

        if prop_type not in bfData.FBX_DATA_BPSTR_TYPES.keys():
            # return string by default
            return bpStr.BpStrData

        prop_data_dict = bfData.FBX_DATA_BPSTR_TYPES[prop_type]

        if prop_type_enum not in prop_data_dict.keys():
            # return string by default
            return bpStr.BpStrData

        return prop_data_dict[prop_type_enum]

    @classmethod
    def get_property_type_str(cls, fbx_property):
        prop_type_enum = fbx_property.GetPropertyDataType().GetType()
        prop_type = type(prop_type_enum)

        if prop_type not in bfData.FBX_PROPERTY_TYPES:
            return "unknownType_{}".format(prop_type)

        prop_enum_names = bfData.FBX_ENUM_NAMES[prop_type]

        if prop_type_enum not in prop_enum_names:
            return "unknownEnum_{}_{}".format(prop_type, prop_type_enum)

        return prop_enum_names[prop_type_enum]


class FbxPropertyQtModel(Qt.QtCore.QAbstractTableModel):
    """
    One should be instanced per FbxObject.
    TODO change this to item model and account for property children
    """

    def __init__(self, *args, **kwargs):
        super(FbxPropertyQtModel, self).__init__(*args, **kwargs)
        self._fbx_object = None
        self._properties = []

        # TODO use class instead of tuple
        self._columns = [
            FbxPropertyColumn(
                "name",
                FbxPropertyColumn.get_property_name,
                None
            ),
            FbxPropertyColumn(
                "value",
                FbxPropertyColumn.get_property_value,
                FbxPropertyColumn.set_property_value
            ),
            FbxPropertyColumn(
                "type",
                FbxPropertyColumn.get_property_type_str,
                None
            )
        ]

    def set_fbx_object(self, fbx_object):
        """
        Requires owner to call model.beginResetModel() before making changes to referenced object
        and self.model.endResetModel() when done.

        model.beginResetModel()
        model.endResetModel()

        """

        self._properties = []

        try:
            prop = fbx_object.GetFirstProperty()

            while prop.IsValid():

                # to get the value of a property,
                # first it must be cast to the appropriate property class
                # the Get() method is not present in the FbxProperty base class.
                # https://forums.autodesk.com/t5/fbx-forum/fbxproperty-get-in-2013-1-python/td-p/4243290
                prop_type_enum = prop.GetPropertyDataType().GetType()
                prop_type = type(prop_type_enum)

                if prop_type in bfData.FBX_PROPERTY_TYPES:
                    prop_type_enums = bfData.FBX_PROPERTY_TYPES[prop_type]
                    prop_enum_names = bfData.FBX_ENUM_NAMES[prop_type]

                    if prop_type_enum in prop_type_enums:
                        prop_class = prop_type_enums[prop_type_enum]

                        # cast property
                        cast_prop = prop_class(prop)
                        self._properties.append(cast_prop)

                    elif prop_type_enum in prop_enum_names:
                        print "Property type not supported: {0} {1}".format(
                            prop.GetName(), prop_enum_names[prop_type_enum]
                        )
                    else:
                        print "Property type enum not supported: {0}".format(
                            prop.GetName()
                        )
                else:
                    print "Property type not supported: {0}".format(
                        prop_type
                    )

#                 print cast_prop.GetName(), cast_prop.Get()
                prop = fbx_object.GetNextProperty(prop)

            self._fbx_object = fbx_object
#             print "props:", self._properties
        except:
            self._properties = []
            self._fbx_object = None

    def rowCount(self, index=None):
        return len(self._properties)

    def columnCount(self, index=None):
        return len(self._columns)

    def data(self, index, role):

        if not index.isValid():
            return

        row = index.row()
        column = index.column()
        fbx_property = self._properties[row]

        if role in [Qt.QtCore.Qt.DisplayRole, Qt.QtCore.Qt.EditRole]:
            column_object = self._columns[column]
            value = column_object.get(fbx_property)
            return value

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
        fbx_property = self._properties[row]

        if role == Qt.QtCore.Qt.EditRole:
            column_object = self._columns[column]
            # todo conversion
            res = column_object.set(fbx_property, value)
            print res
            self.dataChanged.emit(index, index)

            return True

        return False

    def flags(self, index):
        """ hard-coded item flags """
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable | Qt.QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):

        if role == Qt.QtCore.Qt.DisplayRole:
            if orientation == Qt.QtCore.Qt.Horizontal:
                if section < len(self._columns):
                    column_object = self._columns[section]
                    return column_object.name()
                else:
                    return "other"

    def insertColumn(self, *args, **kwargs):
        raise NotImplementedError()

    def insertColumns(self, *args, **kwargs):
        raise NotImplementedError()

    def insertRow(self, *args, **kwargs):
        """TODO add property button!"""
        raise NotImplementedError()

    def insertRows(self, *args, **kwargs):
        raise NotImplementedError()


class FbxSceneQtModel(Qt.QtCore.QAbstractItemModel):

    # define custom role enums for returning specific data to sort by
    #     kSortRole = Qt.QtCore.Qt.UserRole
    kFilterRole = Qt.QtCore.Qt.UserRole + 1

    def __init__(self, fbx_scene, parent=None):
        super(FbxSceneQtModel, self).__init__(parent)

        # TODO be careful for empty pointer if the scene is deleted
        self._fbx_scene = fbx_scene
        self._root_node = self._fbx_scene.GetRootNode()

        # temp way of holding references to FbxNodes to stop them being destroyed
        # TODO find better solution
#         self._nodes = set([])

        self._nodes = {}
        self._node_property_models = {}

    def parent(self, index):
        if not index.isValid():
            return Qt.QtCore.QModelIndex()

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
#         self._nodes.add(node)

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
        return 1

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
            if column == 1:
                return get_fbx_node_attribute_label(node)
            else:
                return "null"

        if role == Qt.QtCore.Qt.DecorationRole:

            if column == 0:
                icon_file = get_fbx_node_attribute_icon(node)

                if icon_file is not None:
                    pixmap = Qt.QtGui.QPixmap(icon_file)
                    icon = Qt.QtGui.QIcon(pixmap)
                    return icon

        # filter by name
        if role == FbxSceneQtModel.kFilterRole:
            return name

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
            else:
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
                if section == 0:
                    return "Name"

        return None

    def insertColumn(self, *args, **kwargs):
        raise NotImplementedError("Use addNode or createNode instead")

    def insertColumns(self, *args, **kwargs):
        raise NotImplementedError("Use addNodes or createNodes instead")

    def insertRow(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNode instead")

    def insertRows(self, *args, **kwargs):
        raise NotImplementedError("Use insertNode or insertNewNodes instead")

    def set_fbx_scene(self, fbx_scene):
        """
        Requires owner to call model.beginResetModel() before making changes to referenced scene
        and self.model.endResetModel() when done.

        TODO see if this can be done here instead.
        However for safety this probably should be called by owner.
        """

        self._fbx_scene = fbx_scene
        self._root_node = self._fbx_scene.GetRootNode()

        print "Root name", self._root_node.GetName()

        self._nodes = {}
        self._node_property_models = {}

        for i in range(fbx_scene.GetNodeCount()):
            node = fbx_scene.GetNode(i)
            node_id = node.GetUniqueID()
            self._nodes[node_id] = node

            if True:
                prop_model = FbxPropertyQtModel()

                prop_model.beginResetModel()
                prop_model.set_fbx_object(node)
                prop_model.endResetModel()

                self._node_property_models[node_id] = prop_model

#         self._nodes = set([])
#         self.update()

#     def update(self):
#         self.dataChanged.emit(
#             Qt.QtCore.QModelIndex(),
#             #             Qt.QtCore.QModelIndex(),
#             self.createIndex(
#                 self._root_node.GetChildCount(True),
#                 len(self._horizontal_headers)
#             )
#             #             self.createIndex(self.rowCount(index), 0)
#         )

#     def addNode(self, node, parent):
#         parent.addChild(node)
#
#         self.dataChanged.emit(
#             Qt.QtCore.QModelIndex(),
#             self.createIndex(self._root_node.childCount(recursive=True), 0)
#         )


class LabeledLineEditWidget(Qt.QtWidgets.QWidget):
    """Simple widget with a label and lineEdit widgets."""

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
    """Test widget to mimic maya channel box or unity inspector."""

    def __init__(self, parent=None):
        super(InspectorWidget, self).__init__(parent)

        self.data_mapper = Qt.QtWidgets.QDataWidgetMapper()

        self.lyt = Qt.QtWidgets.QVBoxLayout()

        # hard code a couple of property widgets
        self.name_widget = LabeledLineEditWidget("name")
        self.name_widget.setEnabled(False)

        # temp
        self.type_widget = LabeledLineEditWidget("type")
        self.type_widget.edit.setReadOnly(True)
        self.type_widget.setEnabled(False)

        self.lyt.addWidget(self.name_widget)
        self.lyt.addWidget(self.type_widget)

        self.setLayout(self.lyt)

    # if using a regular model
    def setModel(self, model):
        self.model = model

        # create widget mapping
        self.data_mapper.setModel(self.model)

    # if using a proxy model for sorting/filtering etc
    def setProxyModel(self, proxy_model):
        self._proxy_model = proxy_model
        self.setModel(proxy_model.sourceModel())

    def add_mapping(self):
        # mapping(widget, column)
        self.data_mapper.addMapping(self.name_widget.edit, 0)
        self.data_mapper.addMapping(self.type_widget.edit, 1)

        # bind mapper to first row in model
#         self.data_mapper.toFirst()

    def setSelection(self, index, old_index):
        if index.isValid():
            self.add_mapping()
            self.data_mapper.setRootIndex(index.parent())
            self.data_mapper.setCurrentModelIndex(index)
            self.name_widget.setEnabled(True)
            self.type_widget.setEnabled(True)
        else:
            self.data_mapper.clearMapping()
            self.name_widget.edit.setText(None)
            self.name_widget.setEnabled(False)
            self.type_widget.edit.setText(None)
            self.type_widget.setEnabled(False)


class HierarchySortFitler(Qt.QtCore.QSortFilterProxyModel):
    """Allows parents of filtered row to remain visible.

    https://stackoverflow.com/questions/250890/using-qsortfilterproxymodel-with-a-tree-model

    """

    HIGHLIGHT_COLOR = Qt.QtGui.QColor(200, 225, 255)

    def __init__(self, *args, **kwargs):
        super(HierarchySortFitler, self).__init__(*args, **kwargs)
        self._highlighted_indices = set([])

    def data(self, index, role):
        """Override source model data method.

        Add background colour for highlited indices.
        """

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
                return self.HIGHLIGHT_COLOR

        else:
            return Qt.QtCore.QSortFilterProxyModel.data(self, index, role)

    def filterAcceptsRow(self, source_row, source_parent):
        # custom behaviour
        if not self.filterRegExp().isEmpty():
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

                # return current match
                return match

        # parent call for initial behaviour
        return Qt.QtCore.QSortFilterProxyModel.filterAcceptsRow(self, source_row, source_parent)

    def set_fbx_scene(self, fbx_scene):
        self.sourceModel().set_fbx_scene(fbx_scene)
        self.update()

    def update(self):
        self.sourceModel().update()


class Gui(Qt.QtWidgets.QMainWindow):

    USE_FILTER = True
    USE_CUSTOM_FILTER = True
    USE_INSPECTOR = True

    def __init__(self, parent=None, file_path=None):
        super(Gui, self).__init__(parent)

        self._filter_value = ""

        self._debug_print = True

        self._file_path = file_path

        # create initial fbx objects
        self._fbx_manager = fbx.FbxManager.Create()
        self._fbx_scene = fbx.FbxScene.Create(
            self._fbx_manager, "untitled scene"
        )

        # create qt objects
        self.setCentralWidget(
            Qt.QtWidgets.QWidget()
        )

        self._create_menu_bar()
        self._create_status_bar()
        self._create_widgets()
        self._create_layout()
        self._create_model()
        self._connect_widgets()

        # if file is given, load it!
        if file_path is not None:
            self._load_fbx()

    def debug(self, msg):
        '''
        print in context
        # TODO proper logging
        '''

        if self._debug_print:
            print msg

        # convert msg to something readable on status bar
        msg = str(msg)
        self.status_bar.showMessage(msg)

    def _new_scene(self, scene_name="untitled scene"):
        # clear selections to clear all connected widgets etc.
        self.tree.selectionModel().clearSelection()

        # inform Qt objects we are about to change the scene
        self.model.beginResetModel()

        # clear old objects
        self._fbx_manager.Destroy()
        del self._fbx_manager, self._fbx_scene

        # make new objects
        self._fbx_manager = fbx.FbxManager.Create()
        self._fbx_scene = fbx.FbxScene.Create(
            self._fbx_manager, scene_name
        )

        # inform Qt objects we are done changing the scene
        self.model.set_fbx_scene(self._fbx_scene)
        self.model.endResetModel()

        # set title
        self.setWindowTitle(scene_name)

    def _load_fbx(self):
        # clear selections to clear all connected widgets etc.
        self.tree.selectionModel().clearSelection()

        # inform Qt objects we are about to change the scene
        self.model.beginResetModel()

        # clear old objects
        self._fbx_manager.Destroy()
        del self._fbx_manager, self._fbx_scene

        # create new objects
        self._fbx_manager = fbx.FbxManager.Create()

        io_settings = fbx.FbxIOSettings.Create(self._fbx_manager, fbx.IOSROOT)
        self._fbx_manager.SetIOSettings(io_settings)

        fbx_importer = fbx.FbxImporter.Create(self._fbx_manager, "")

        # Use the first argument as the filename for the importer.
        try:
            fbx_importer.Initialize(
                self._file_path, -1, self._fbx_manager.GetIOSettings()
            )
        except Exception as err:
            msg = "Call to FbxImporter::Initialize() failed.\n"
            msg += "Error returned: {0}".format(
                fbx_importer.GetStatus().GetErrorString()
            )
            print msg
            raise err

        # create scene
        self._fbx_scene = fbx.FbxScene.Create(
            self._fbx_manager,
            #             self._file_path
            os.path.basename(self._file_path).split(".")[0]
        )

        fbx_importer.Import(self._fbx_scene)
        fbx_importer.Destroy()

        # inform Qt objects we are done changing the scene
        self.model.set_fbx_scene(self._fbx_scene)
        self.model.endResetModel()

        # set title
#         print self._fbx_scene.GetName()
        self.setWindowTitle(self._file_path)

#         if self.USE_CUSTOM_FILTER:
#             self._proxy_model.set_fbx_scene(self._fbx_scene)
# #             self._proxy_model.update()
#         else:
#             self.model.set_fbx_scene(self._fbx_scene)
# #             self.model.update()

    def _save_fbx_file(self):
        # TODO validate manager and scene

        if True:
            # save file using FbxCommon
            res = FbxCommon.SaveScene(
                self._fbx_manager, self._fbx_scene, self._file_path
            )
            self.debug("FbxCommon.SaveScene() res: {}".format(res))
        else:
            # export file using exporter

            # TODO manage settings via gui
            io_settings = fbx.FbxIOSettings.Create(
                self._fbx_manager, fbx.IOSROOT)
            self._fbx_manager.SetIOSettings(io_settings)

            exporter = fbx.FbxExporter.Create(self._fbx_manager, "")

            try:
                exporter.Initialize(
                    self._file_path, -1, self._fbx_manager.GetIOSettings()
                )
            except Exception as err:
                msg = "Call to FbxExporter::Initialize() failed.\n"
                msg += "Error returned: {0}".format(
                    exporter.GetStatus().GetErrorString()
                )
                self.debug(msg)
                raise err

            exporter.Export(self._fbx_scene)
            exporter.Destroy()

        self.setWindowTitle(self._file_path)

    def _create_menu_bar(self):
        self.menubar = self.menuBar()

        file_menu = self.menubar.addMenu('&File')

        # new menu item/ shortcut

        new_action = Qt.QtWidgets.QAction(Qt.QtGui.QIcon(), '&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New scene')
        new_action.triggered.connect(self._new_scene)

        file_menu.addAction(new_action)

        # open menu item/ shortcut
        open_icon = self.style().standardIcon(
            Qt.QtWidgets.QStyle.SP_DialogOpenButton
        )

        open_action = Qt.QtWidgets.QAction(open_icon, '&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open fbx file')
        open_action.triggered.connect(self._open_fbx_file_dialog)

        file_menu.addAction(open_action)

        # TODO import/merge

        # import menu item/ shortcut
#         import_icon = self.style().standardIcon(
#             Qt.QtWidgets.QStyle.SP_DialogOpenButton
#         )

        import_action = Qt.QtWidgets.QAction(Qt.QtGui.QIcon(), '&Import', self)
        import_action.setShortcut('Ctrl+I')  # TODO check what this should be
        import_action.setStatusTip('Import fbx file')
#         import_action.triggered.connect(self._import_fbx_file)

        file_menu.addAction(import_action)

        # import menu item/ shortcut
#         import_icon = self.style().standardIcon(
#             Qt.QtWidgets.QStyle.SP_DialogOpenButton
#         )

        merge_action = Qt.QtWidgets.QAction(Qt.QtGui.QIcon(), '&Merge', self)
        # TODO check what this should be
        merge_action.setShortcut('Ctrl+Shift+I')
        merge_action.setStatusTip('Merge fbx file')
#         merge_action.triggered.connect(self._merge_fbx_file)

        file_menu.addAction(merge_action)

        # save menu item/ shortcut
        save_icon = self.style().standardIcon(
            Qt.QtWidgets.QStyle.SP_DialogSaveButton
        )

        save_action = Qt.QtWidgets.QAction(open_icon, '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save fbx file')
#         save_as_action.triggered.connect(self._save_as_fbx_file_dialog)

        file_menu.addAction(save_action)

        # save as menu item/ shortcut
        save_icon = self.style().standardIcon(
            Qt.QtWidgets.QStyle.SP_DialogSaveButton
        )

        save_as_action = Qt.QtWidgets.QAction(open_icon, '&Save As', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.setStatusTip('Save as fbx file')
        save_as_action.triggered.connect(self._save_as_fbx_file_dialog)

        file_menu.addAction(save_as_action)

        # exit menu item/ shortcut
        exit_action = Qt.QtWidgets.QAction(Qt.QtGui.QIcon(), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(
            Qt.QtWidgets.QApplication.instance().quit
        )

        file_menu.addAction(exit_action)

    def _create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

    def _open_fbx_file_dialog(self):
        file_path, file_type = Qt.QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open file',
            self._file_path,
            "fbx files (*.fbx)"
        )

        self.debug(file_path)

        if os.path.exists(file_path):
            self._file_path = file_path
            self._load_fbx()
#             self._update_data()

    def _save_as_fbx_file_dialog(self):
        file_path, file_type = Qt.QtWidgets.QFileDialog.getSaveFileName(
            self,
            'Save file',
            self._file_path,
            "Fbx files (*.fbx)"
        )

        self.debug("Attempting to save file: {}".format(file_path))

        if os.path.exists(file_path):
            self.debug(['overwriting ', file_path])

        old_file_path = str(self._file_path)

        self._file_path = file_path

        try:
            self._save_fbx_file()
            self.debug("File saved as: {}".format(file_path))
        except:  # something?
            self.debug("Failed to save as: {}".format(file_path))
            self._file_path = old_file_path

        # self.load_ply()
        # self.update_data()

    def _create_widgets(self):
        """
        table view selection/edit options:
        https://stackoverflow.com/questions/18831242/qt-start-editing-of-cell-after-one-click

        Constant    Value   Description
        QAbstractItemView::NoEditTriggers   0   No editing possible.
        QAbstractItemView::CurrentChanged   1   Editing start whenever current item changes.
        QAbstractItemView::DoubleClicked    2   Editing starts when an item is double clicked.
        QAbstractItemView::SelectedClicked  4   Editing starts when clicking on an already selected item.
        QAbstractItemView::EditKeyPressed   8   Editing starts when the platform edit key has been pressed over an item.
        QAbstractItemView::AnyKeyPressed    16  Editing starts when any key is pressed over an item.
        QAbstractItemView::AllEditTriggers  31  Editing starts for all above actions.

        """

        # node selection tree
        self.tree = Qt.QtWidgets.QTreeView()
        self.tree.setIndentation(10)
        self.tree.setSelectionMode(
            Qt.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        # property table
        self.property_table_view = Qt.QtWidgets.QTableView()

#         self.property_table_view.setEditTriggers(
#             Qt.QtWidgets.QAbstractItemView.AllEditTriggers
#         )

        # inspector
        if self.USE_INSPECTOR:
            self.inspector_widget = InspectorWidget()

        # tree filter
        if self.USE_FILTER:
            self.filter_box = Qt.QtWidgets.QLineEdit()

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout(self.centralWidget())

        self.lyt_splitter = Qt.QtWidgets.QSplitter()
#         self.lyt_splitter.setHandleWidth(1)
#         self.lyt_splitter.setRubberBand(100)

        self.hierarchy_widget = Qt.QtWidgets.QWidget()
        self.hierarchy_lyt = Qt.QtWidgets.QVBoxLayout()
        self.hierarchy_widget.setLayout(self.hierarchy_lyt)

        self.property_widget = Qt.QtWidgets.QWidget()
        self.property_lyt = Qt.QtWidgets.QVBoxLayout()
        self.property_widget.setLayout(self.property_lyt)

        self.lyt_splitter.addWidget(self.hierarchy_widget)
        self.lyt_splitter.addWidget(self.property_widget)

        self.lyt_splitter.setSizes([50, 100])

        self.lyt.addWidget(self.lyt_splitter)

#         self.lyt.addLayout(self.hierarchy_lyt)
#         self.lyt.addLayout(self.property_lyt)

        if self.USE_FILTER:
            self.hierarchy_lyt.addWidget(self.filter_box)

        self.hierarchy_lyt.addWidget(self.tree)

        if self.USE_INSPECTOR:
            self.property_lyt.addWidget(self.inspector_widget)

        self.property_lyt.addWidget(self.property_table_view)

    def _create_model(self):
        """Create fbx scene model and filters.
        """

        self.model = FbxSceneQtModel(self._fbx_scene)

        if self.USE_FILTER:

            if self.USE_CUSTOM_FILTER:
                self._proxy_model = HierarchySortFitler()
            else:
                self._proxy_model = Qt.QtCore.QSortFilterProxyModel()

            # set filter options
            self._proxy_model.setFilterCaseSensitivity(
                Qt.QtCore.Qt.CaseSensitivity.CaseInsensitive)

            self._proxy_model.setSourceModel(self.model)

            # set our custom role enum to be called when sending sortRole to
            # things
#             self._proxy_model.setSortRole(FbxSceneQtModel.kSortRole)
#             self._proxy_model.setFilterRole(FbxSceneQtModel.kFilterRole)

    def _connect_widgets(self):

        if self.USE_FILTER:
            self.tree.setModel(self._proxy_model)
            self.filter_box.textChanged.connect(self._filter_edit_changed)

            if True:
                # TESTING
                self._completer = Qt.QtWidgets.QCompleter()
                self._completer.setModel(self.model)
                self._completer.setCaseSensitivity(
                    Qt.QtCore.Qt.CaseSensitivity.CaseInsensitive)
                self.filter_box.setCompleter(self._completer)
        else:
            self.tree.setModel(self.model)

        # connect node selection
        Qt.QtCore.QObject.connect(
            self.tree.selectionModel(),
            SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
            self._tree_current_changed
        )

        Qt.QtCore.QObject.connect(
            self.tree.selectionModel(),
            SIGNAL("selectionChanged(QItemSelection, QItemSelection)"),
            self._tree_selection_changed
        )

#         # connect propety table sorting
#         # TODO decide if we want this?
#         self.check_box.stateChanged.connect(
#             self.property_table_view.setSortingEnabled
#         )

        # connect inspector model
        # note: because the model is persistent and will be updated with new scenes,
        # this should never need to be changed.
        if self.USE_INSPECTOR:
            if self.USE_FILTER:
                self.inspector_widget.setProxyModel(self._proxy_model)
            else:
                self.inspector_widget.setModel(self.model)

    def _tree_selection_changed(self, new_selected, new_deselected):
        """Update widgets with multiple or empty index selections.
        Normally called before self._tree_current_changed().
        """
        selected = self.tree.selectionModel().selection()

        if len(selected):
            pass
#             # get last selected index
#             #             index = selected.indexes()[-1]
#             index = self.tree.selectionModel().currentIndex()
#
#             if self.USE_FILTER:
#                 index = self._proxy_model.mapToSource(index)
# #                 old_index = self._proxy_model.mapToSource(old_index)
#
#             self._set_property_table_view_index(index, None)
#
#             if self.USE_INSPECTOR:
#                 self.inspector_widget.setSelection(index, None)
        else:
            # set invalid index to indicate empty selection
            invalid_index = Qt.QtCore.QModelIndex()

            self._set_property_table_view_index(invalid_index, None)

            if self.USE_INSPECTOR:
                self.inspector_widget.setSelection(invalid_index, None)

    def _tree_current_changed(self, index, old_index):
        """Update corresponding widgets to current selected index.
        Normally called after self._tree_selection_changed().
        """

        if self.USE_FILTER:
            index = self._proxy_model.mapToSource(index)
            old_index = self._proxy_model.mapToSource(old_index)

        self._set_property_table_view_index(index, old_index)

        if self.USE_INSPECTOR:
            self.inspector_widget.setSelection(index, old_index)

    def _filter_edit_changed(self):
        # get filter value
        value = self.filter_box.text()

        # reset highlighted indices and set new filter
        if self.USE_CUSTOM_FILTER:
            self._proxy_model._highlighted_indices.clear()

        self._proxy_model.setFilterWildcard(value)

        # show all results
        self.tree.expandAll()

    def _set_property_table_view_index(self, index, old_index):
        """
        Set proprty_table_view model to node property model.
        """
        if not index.isValid():
            self.property_table_view.setModel(None)
            return

        node = index.internalPointer()
        node_id = node.GetUniqueID()
        prop_model = self.model._node_property_models[node_id]
        self.property_table_view.setModel(prop_model)

    def destroy(self, *args, **kwargs):
        """Never run?"""
        # destroy fbx objects
        self._fbx_manager.Destroy()
        del self._fbx_manager  # , fbx_scene

        return Qt.QtWidgets.QWidget.destroy(self, *args, **kwargs)


if __name__ == "__main__":

    app = Qt.QtWidgets.QApplication(sys.argv)

    gui = Gui(file_path=TEST_FILE)
    gui.show()

    sys.exit(app.exec_())
