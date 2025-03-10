"""Dynamic item implementation for FbxConnections
Start with object connection widget and go from there...


** DEPRICATED **

See bfConnectionUtilityItems


"""


from brenpy.core import bpCore
from brenfbx.core import bfEnvironment
from brenpy.qt.core.bpQtImportUtils import QtWidgets

from brenpy.qt.widgets import bpQtCollapsibleWidgets
from brenpy.core import bpDebug

# from brenfbx.qt.connection import bfQtConnectionModels
from brenfbx.qt.connection import bfQtConnectionItemModels
from brenfbx.qt.property import bfQtPropertyModels
from brenfbx.items import bfPropertyItems
from brenfbx.items import bfSceneItems
from brenfbx.qt import bfQtCore
from brenfbx.qt.scene import bfQtSceneModels

from brenfbx.qt.dialog import bfQtObjectDialogs
from brenfbx.qt.dialog import bfQtPropertyDialogs

from brenfbx.qt import bfQtWidgets
from brenpy.qt.item.widgets import bpQtItemsWidgets
from brenfbx.items import bfConnectionItems


class BfConnectionViewBase(
    bfQtWidgets.BfQWidgetBase,
    bpQtItemsWidgets.BpQItemUndoTreeView
):
    """TODO/WIP
    """

    def __init__(self, *args, **kwargs):
        super(BfConnectionViewBase, self).__init__(*args, **kwargs)


    def create_selection_dialog(self, parent):
        """Overridable method"""
        raise bfQtCore.BfQtError(
            "Cannot create selection dialog from connection view base class"
        )

    def _create_clicked(self):
        """Overridable method
        """

        create_dialog = self.create_selection_dialog(parent=self)

        if False:
            # this method is thread safe
            # but continues code before user has
            # entered data
            create_dialog.setModal(True)
            create_dialog.show()
        else:
            # using this method blocks code from continuing
            # until user has finished entering data
            create_dialog.exec_()

        if create_dialog.value() is None:
            self.debug("Object not recognised: {}".format(
                create_dialog.text(), self.LEVELS.user
            ))

        else:
            fbx_obj = create_dialog.value()

            result = self.model().create_connection(fbx_obj)

            if result:
                self.debug("Connection successful: {}".format(
                    fbx_obj.GetName(), self.LEVELS.user
                ))
            else:
                self.debug("Connection failed: {}".format(
                    fbx_obj.GetName(), self.LEVELS.user
                ))

            self.emit_refresh_request()

        # print "ABOUT TO RESTORE"
        # self.restore_view_state()

    # def _disconnect_selected(self):
    #     """
    #     """
    #     # self.store_view_state()
    #
    #     selected_indices = self.get_selected_connection_indices()
    #
    #     self.selectionModel().clearSelection()
    #
    #     self.model().removeIndices(selected_indices)
    #
    #     self.emit_refresh_request()
    #
    #     # self.restore_view_state()

    def _disconnect_all(self):
        """
        TODO confirmation dialog (or undo?)
        """

        self.selectionModel().clearSelection()

        self.model().fbx_disconnect_all()

        self.emit_refresh_request()

        return True

    # def _refresh(self):
    #     """
    #     TODO figure out why this is throwing errors!
    #         File "D:\Repos\brenfbxpy\python\brenfbx\qt\connection\bfConnectionWidgets.py", line 144, in model
    #         model = super(BfConnectionViewBase, self).model()
    #         RuntimeError: Internal C++ object (BfObjectConnectionsTableView) already deleted.
    #
    #     """
    #     super(BfConnectionViewBase, self)._refresh()
    #
    #     if self.model() is None:
    #         return
    #
    #     self.model().beginResetModel()
    #     self.model().endResetModel()


class BfPropertyConnectionsTreeView(BfConnectionViewBase):
    """
    """

    def __init__(self, *args, **kwargs):
        super(BfPropertyConnectionsTreeView, self).__init__( *args, **kwargs)


    def create_selection_dialog(self, parent):
        item_manager = bfPropertyItems.BfFbxPropertySceneTreeItemManager(
            bf_app=self.bf_environment(),
            # fbx_scene=self.model().get_fbx_scene()
            fbx_scene=self.bf_environment().scene_model().get_fbx_scene()
        )

        model = bfQtPropertyModels.BfFbxPropertyModel()
        model.set_item_manager(item_manager)

        return bfQtPropertyDialogs.BFbxPropertySelectionDialog(
            model, parent=parent
        )


class BfObjectConnectionsTreeView(BfConnectionViewBase):
    """
    """

    def __init__(self,  *args, **kwargs):
        super(BfObjectConnectionsTreeView, self).__init__( *args, **kwargs)

    # def setModel(self, model):
    #     """TODO check model
    #     """
    #
    #     if not isinstance(
    #             model, (
    #                     bfQtConnectionModels.BFbxObjectConnectionsModelBase,
    #                     NoneType
    #             )
    #     ):
    #         raise bfQtCore.BfQtError(
    #             "Model must be object connections model: {}".format(
    #                 model
    #             )
    #         )
    #
    #     res = super(BfObjectConnectionsTreeView, self).setModel(model)
    #     return res

    def create_selection_dialog(self, parent):

        item_manager = bfSceneItems.FbxSceneItemManager(bf_app=self.bf_environment())
        item_manager.set_fbx_scene(self.bf_environment().scene_model().get_fbx_scene())

        model = bfQtSceneModels.BfFbxSceneModel()
        model.set_item_manager(item_manager)

        return bfQtObjectDialogs.BFbxObjectSelectionDialog(
            model, parent=parent
        )


class BfConnectionGroupWidget(
    # bpQtWidgets.BpCollapsibleWidget
    # bpQtWidgets.BpRefreshableWidgetBase,
    bfEnvironment.BfEnvironmentDependant,
    bpQtCollapsibleWidgets.BpCollapsibleWidget
):

    def __init__(self, *args, **kwargs):

        label = bpCore.parse_kwarg("label", kwargs, default_value="connections")
        kwargs["label"] = label

        super(BfConnectionGroupWidget, self).__init__(*args, **kwargs)

        # self._manager = None
        self._views_connected = False

        self._src_object_view = None
        self._src_property_view = None
        self._dst_object_view = None
        self._dst_property_view = None

        self.create_item_managers()
        self.create_models()
        self.create_views()

        self.connect_models()
        self.connect_views()
        #         self.create_tab_layout()
        #         self.create_flat_tab_layout()
        #         self.create_staggered_tab_layout()
        #         self.create_src_dst_tab_layout()
        self.create_collapsable_layout()

    #         self.setGeometry(
    #             QtWidgets.QApplication.desktop().screenGeometry().width() * 0.3,
    #             QtWidgets.QApplication.desktop().screenGeometry().height() * 0.3,
    #             400,
    #             400
    #         )

    def create_item_managers(self):

        self._src_objects_manager = bfConnectionItems.BfFbxSrcObjectsManager(bf_app=self.bf_environment())
        self._src_properties_manager = bfConnectionItems.BfFbxSrcPropertiesManager(bf_app=self.bf_environment())
        self._dst_objects_manager = bfConnectionItems.BfFbxDstObjectsManager(bf_app=self.bf_environment())
        self._dst_properties_manager = bfConnectionItems.BfFbxDstPropertiesManager(bf_app=self.bf_environment())

    def connection_managers(self):
        return [
            self._src_objects_manager,
            self._src_properties_manager,
            self._dst_objects_manager,
            self._dst_properties_manager,
        ]

    def create_models(self):
        self._src_objects_model = bfQtConnectionItemModels.BFbxObjectConnectionsModelBase(
            bf_app=self.bf_environment()
        )

        self._src_properties_model = bfQtConnectionItemModels.BFbxPropertyConnectionsModelBase(
            bf_app=self.bf_environment()
        )

        self._dst_objects_model = bfQtConnectionItemModels.BFbxObjectConnectionsModelBase(
            bf_app=self.bf_environment()
        )

        self._dst_properties_model = bfQtConnectionItemModels.BFbxPropertyConnectionsModelBase(
            bf_app=self.bf_environment()
        )

    def connect_models(self):
        for manager, model in zip(self.connection_managers(), self.connection_models()):
            model.set_item_manager(manager)

        return True

    # def create_models(self):
    #     self._src_objects_model = bfQtConnectionModels.BFbxSrcObjectsModel(bf_app=self.bf_environment())
    #     self._src_properties_model = bfQtConnectionModels.BFbxSrcPropertiesModel(bf_app=self.bf_environment())
    #     self._dst_objects_model = bfQtConnectionModels.BFbxDstObjectsModel(bf_app=self.bf_environment())
    #     self._dst_properties_model = bfQtConnectionModels.BFbxDstPropertiesModel(bf_app=self.bf_environment())

    def connection_models(self):
        return [
            self._src_objects_model,
            self._src_properties_model,
            self._dst_objects_model,
            self._dst_properties_model,
        ]

    def set_connected_obj(self, value):

        for model in self.connection_models():
            model.set_connected_obj(value)

    def disconnect_views(self):
        for view in self.connection_views():
            view.setModel(None)

        self._views_connected = False

    def connect_views(self):
        for model, view in [
            (self._src_objects_model, self._src_object_view),
            (self._src_properties_model, self._src_property_view),
            (self._dst_objects_model, self._dst_object_view),
            (self._dst_properties_model, self._dst_property_view),
        ]:
            view.setModel(model)

            # we only need the views to be refreshable and debuggable
            # no need to include their containing widgets etc.
            self.add_refreshable_widget(view)
            self.add_debug_object(view)

        self._views_connected = True

    def views_connected(self):
        return self._views_connected

    def create_views(self):
        """Stuff
        """

        self._src_object_view = BfObjectConnectionsTreeView(bf_app=self.bf_environment())#, parent=self)
        self._src_property_view = BfPropertyConnectionsTreeView(bf_app=self.bf_environment())#, parent=self)
        self._dst_object_view = BfObjectConnectionsTreeView(bf_app=self.bf_environment())#, parent=self)
        self._dst_property_view = BfPropertyConnectionsTreeView(bf_app=self.bf_environment())#, parent=self)

        self._con_label = QtWidgets.QLabel("Connections")

        # for widget in self.connection_views():
        #     self.add_widget(widget)

    def connection_views(self):
        return [
            self._src_object_view,
            self._src_property_view,
            self._dst_object_view,
            self._dst_property_view,
        ]

    def create_debug_layout(self):
        self._lyt = QtWidgets.QHBoxLayout()
        self.setLayout(self._lyt)

        self._con_lyt = QtWidgets.QHBoxLayout()

        self._lyt.addLayout(self._con_lyt)

        for view in self.connection_views():
            self._con_lyt.addWidget(view)


    def create_collapsable_layout(self):
        # self.setOrientation(QtCore.Qt.Vertical)

        # self._so_widget = bpQtWidgets.BpCollapsibleWidget(label="Src Objects")
        # self._sp_widget = bpQtWidgets.BpCollapsibleWidget(label="Src Properties")
        # self._do_widget = bpQtWidgets.BpCollapsibleWidget(label="Dst Objects")
        # self._dp_widget = bpQtWidgets.BpCollapsibleWidget(label="Dst Properties")

        self._so_widget = bpQtCollapsibleWidgets.BpCollapsibleWidget(label="Src Objects")
        self._sp_widget = bpQtCollapsibleWidgets.BpCollapsibleWidget(label="Src Properties")
        self._do_widget = bpQtCollapsibleWidgets.BpCollapsibleWidget(label="Dst Objects")
        self._dp_widget = bpQtCollapsibleWidgets.BpCollapsibleWidget(label="Dst Properties")

        for view in self.connection_views():
            view.setFixedHeight(100)

        self._so_widget.add_widget(self._src_object_view, show_handle=False)
        self._sp_widget.add_widget(self._src_property_view, show_handle=False)
        self._do_widget.add_widget(self._dst_object_view, show_handle=False)
        self._dp_widget.add_widget(self._dst_property_view, show_handle=False)

        for widget in [
            self._so_widget,
            self._sp_widget,
            self._do_widget,
            self._dp_widget
        ]:
            # widget.show()
            self.add_widget(widget)
            widget.set_minimum_height(113)

        # collapse dst widgets by default
        self._do_widget.collapse()
        self._dp_widget.collapse()

    def _refresh(self):
        super(BfConnectionGroupWidget, self)._refresh()

        for model in self.connection_models():
            model.beginResetModel()
            model.endResetModel()


class Test1(object):
    def __init__(self, base):
        super(Test1, self).__init__()

        self._object_1 = base._scene.FindSrcObject("object1")

        self._src_objects_manager = bfConnectionItems.BfFbxSrcObjectsManager(bf_app=base.bf_environment())

        self._src_objects_model = bfQtConnectionItemModels.BFbxObjectConnectionsModelBase(
            bf_app=base.bf_environment()
        )

        self._src_objects_model.set_item_manager(self._src_objects_manager)
        self._src_objects_model.set_connected_obj(self._object_1)

        self._src_objects_model.set_debug_levels(self._src_objects_model.LEVELS.all())

        self._src_object_view = BfObjectConnectionsTreeView(bf_app=base.bf_environment())

        self._src_object_view.setModel(self._src_objects_model)

        self._src_object_view.show()

        self._src_object_view.setGeometry(
            100,
            100,
            300,
            500
        )

class Test2(
    bpQtCollapsibleWidgets.BpCollapsibleWidget
):
    """Test connection group widget
    """

    def __init__(self, base, parent=None):
        super(Test2, self).__init__(label="test", parent=parent)

        self.base = base

        self._object_1 = base._scene.FindSrcObject("object1")
        self._property_0 = self._object_1.GetFirstProperty()

        self._create_widgets()

        self.add_widget(self.obj_con_widget)
        self.add_widget(self.prop_con_widget)

        self.setGeometry(
            500,
            100,
            300,
            500
        )

        self.show()

    def _create_widgets(self):
        self.obj_con_widget = BfConnectionGroupWidget(
            bf_app=self.base.bf_environment(),
            label="object connections",
            debug_level=bpDebug.DebugLevel.all()
        )

        self.prop_con_widget = BfConnectionGroupWidget(
            bf_app=self.base.bf_environment(),
            label="property connections",
            debug_level=bpDebug.DebugLevel.all()
        )

        # self.obj_con_widget.set_fbx_manager(self._fbx_manager)
        # self.prop_con_widget.set_fbx_manager(self._fbx_manager)

        self.obj_con_widget.set_connected_obj(self._object_1)

        self.prop_con_widget.set_connected_obj(self._property_0)


class Test3(object):
    def __init__(self, base):
        super(Test3, self).__init__()

        self._object_1 = base._scene.FindSrcObject("object1")

        self.obj_con_widget = BfConnectionGroupWidget(
            bf_app=base.bf_environment(), label="object connections", debug_level=bpDebug.DebugLevel.all()
        )

        self.obj_con_widget.set_connected_obj(self._object_1)
        self.obj_con_widget.show()

        self.obj_con_widget.setGeometry(
            1000,
            100,
            300,
            500
        )


class Test4(object):
    def __init__(self, base):
        super(Test4, self).__init__()

        self._object_1 = base._scene.FindSrcObject("object1")

        self._src_objects_manager = bfConnectionItems.BfFbxSrcObjectsManager(bf_app=base.bf_environment())

        self._src_objects_model = bfQtConnectionItemModels.BFbxObjectConnectionsModelBase(
            bf_app=base.bf_environment()
        )

        self._src_objects_model.set_item_manager(self._src_objects_manager)
        self._src_objects_model.set_connected_obj(self._object_1)

        self._src_object_view = BfObjectConnectionsTreeView(bf_app=base.bf_environment())
        self._src_object_view.setModel(self._src_objects_model)

        self._so_widget = bpQtCollapsibleWidgets.BpCollapsibleWidget(label="Src Objects")
        self._so_widget.add_widget(self._src_object_view, show_handle=False)

        self._so_widget.show()

        self._so_widget.setGeometry(
            1500,
            100,
            300,
            500
        )

if __name__ == "__main__":
    import sys
    import os
    # from brenfbx.utils import bfEnvironmentUtils
    from brenfbx.utils import bfSceneEnvironmentUtils

    DUMP_DIR = r"D:\Repos\dataDump\brenfbx"
    TEST_FILE = "brenfbx_test_scene_01.fbx"

    # base = bfEnvironmentUtils.BfTestBase(file_path=os.path.join(DUMP_DIR, TEST_FILE))
    base = bfSceneEnvironmentUtils.BfSceneTestBase(
        file_path=os.path.join(DUMP_DIR, TEST_FILE),
        use_custom_objects=False,
        use_qt=True
    )

    app = QtWidgets.QApplication(sys.argv)

    test_1 = Test1(base)
    # test_2 = Test2(base)
    # test_3 = Test3(base)
    # test_4 = Test4(base)

    sys.exit(app.exec_())
