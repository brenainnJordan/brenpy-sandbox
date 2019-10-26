'''

@author: Bren
'''

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


DEFAULT_LABEL_WIDTH = 50


class BfMappedWidget(Qt.QtWidgets.QWidget):
    """Stuff"""

    def __init__(self, parent=None):
        super(BfMappedWidget, self).__init__(parent)

        self._mapped = False

        self._data_mapper = Qt.QtWidgets.QDataWidgetMapper()

        self.setFixedHeight(20)

        self._create_widgets()
        self._create_layout()

    def _create_widgets(self):
        pass

    def _create_layout(self):
        pass

    def setModel(self, model):
        self.model = model

        self._data_mapper.setModel(self.model)
#         self.map_to_index()

    def add_mappings(self):
        pass
#         self.data_mapper.toFirst()

    def setSelection(self, index):
        if not index.isValid():
            self.clear()
            return

        if not self._mapped:
            self.add_mappings()
            self._mapped = True

        self._data_mapper.setRootIndex(index.parent())
        self._data_mapper.setCurrentModelIndex(index)

    def clear(self):
        self._data_mapper.clearMapping()
        self._mapped = False
        self.clear_widgets()

    def clear_widgets(self):
        pass

    def get_current_index(self):
        parent_index = self._data_mapper.rootIndex()
        row = self._data_mapper.currentIndex()
        index = self.model.index(row, 0, parent_index)
        return index


class BfObjectNameWidget(BfMappedWidget):
    """Stuff
    TODO if index is not editable, set line edit to be not editable.
    """

    def __init__(self, parent=None):
        super(BfObjectNameWidget, self).__init__(parent)

    def _create_widgets(self):
        self._label = Qt.QtWidgets.QLabel("Name")
        self._line_edit = Qt.QtWidgets.QLineEdit()
        self._label.setFixedWidth(DEFAULT_LABEL_WIDTH)
        self._line_edit.setEnabled(False)

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.lyt.setContentsMargins(0, 0, 0, 0)
#         self.lyt.setSpacing(5)

        self.lyt.addWidget(self._label)
        self.lyt.addWidget(self._line_edit)
        self.setLayout(self.lyt)

    def add_mappings(self):
        self._line_edit.setEnabled(True)
        self._data_mapper.addMapping(self._line_edit, 0)
        self._data_mapper.toFirst()

    def clear_widgets(self):
        self._line_edit.setText("")
        self._line_edit.setEnabled(False)


class BfObjectTypeWidget(BfMappedWidget):
    """Stuff"""

    def __init__(self, parent=None):
        super(BfObjectTypeWidget, self).__init__(parent)

    def _create_widgets(self):
        self.type_label = Qt.QtWidgets.QLabel("Type")
        self.pixmap_label = Qt.QtWidgets.QLabel()
        self.text_label = Qt.QtWidgets.QLabel()
        self.type_label.setFixedWidth(DEFAULT_LABEL_WIDTH)
        self.pixmap_label.setFixedWidth(20)

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QHBoxLayout()
        self.lyt.setContentsMargins(0, 0, 0, 0)
#         self.lyt.setSpacing(5)

        self.lyt.addWidget(self.type_label)
        self.lyt.addWidget(self.pixmap_label)
        self.lyt.addWidget(self.text_label)
        self.setLayout(self.lyt)

    def add_mappings(self):
        self._data_mapper.addMapping(self.pixmap_label, 2, "pixmap")
        self._data_mapper.addMapping(self.text_label, 1, "text")

    def clear_widgets(self):
        self.text_label.setText("")
        self.pixmap_label.setPixmap(None)
