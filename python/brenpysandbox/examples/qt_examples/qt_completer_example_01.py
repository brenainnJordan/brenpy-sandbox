"""
https://doc.qt.io/qt-5/qtwidgets-tools-completer-example.html

"""

import sys
import os

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


class FileSystemModel(Qt.QtWidgets.QFileSystemModel):
    """
    Note the QFileSystemModel is very powerful,
    with many useful operating system methods.
    """

    kCompleterRole = Qt.QtCore.Qt.UserRole

    def __init__(self, parent=None):
        super(FileSystemModel, self).__init__(parent=parent)

    def data(self, index, role):
        """
        The data() function is reimplemented in order to get it to
        return the entire file parth for the display role.

        For example, with a QFileSystemModel, you will see "Program Files" in the view.
        However, with FileSystemModel, you will see "C:\Program Files".

        """
#         if role in [FileSystemModel.kCompleterRole]:
#             if index.column() == 0:
#
#                 path = Qt.QtCore.QDir.toNativeSeparators(
#                     self.filePath(index)
#                 )
#
#                 if path.endswith(
#                     Qt.QtCore.QDir.separator()
#                 ):
#                     path = path[:-1]
#
#                 return path

        return super(FileSystemModel, self).data(
            index, role
        )


class CustomCompleter(Qt.QtWidgets.QCompleter):
    def __init__(self, *args, **kwargs):
        """Redundant QCompleter subclass.

        Docstrings for convenience.

        QCompleter is pre-configured to work natively with QFileSystemModel.
        So no overrides are necessary in this case.

        Note that filterMode is not available in python.

        See other examples that use custom proxy models
        to replicate this behaviour.
        (TODO find my example)

        """
        super(CustomCompleter, self).__init__(*args, **kwargs)

#         print self.filterMode

#         self.setFilterMode(
#             Qt.QtCore.Qt.MatchContains
#         )

#         return QtGui.QCompleter.__init__(self)

    def splitPath(self, path):
        """Splits the given path into strings that are used to match at each level in the model().

        The default implementation of splitPath() splits a file system path based
        on QDir::separator() when the sourceModel() is a QFileSystemModel.

        When used with list models, the first item in the returned list is used for matching.
        """
        return super(CustomCompleter, self).splitPath(path)

    def pathFromIndex(self, completer_index):
        """Returns the path for the given index.

        The completer object uses this to obtain the completion text from the underlying model.

        The default implementation returns the edit role of the item for list models.

        It returns the absolute file path if the model is a QFileSystemModel.

        """
        src_index = self.completionModel().mapToSource(completer_index)

        return super(CustomCompleter, self).pathFromIndex(completer_index)
#         filter_model = filter_index.model()
#
#         list_index = filter_model.mapToSource(filter_index)
#
#         list_model = list_index.model()
#
#         src_index = list_model.mapToSource(list_index)
#
#         session_model = list_model.sourceModel()
#
#         fbx_object = session_model.get_fbx_object(src_index)
#
#         path_str = str(fbx_object.GetName())
#
#         return path_str


class TestWidget(Qt.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)

        # create model
        self._model = FileSystemModel()

        self._model.setRootPath(
            Qt.QtCore.QDir.fromNativeSeparators(
                r"D:\Repos\dataDump"
            )
        )

        # create widgets
        self._view = Qt.QtWidgets.QTreeView()
        self._view.setModel(self._model)

        self._line_edit = Qt.QtWidgets.QLineEdit()

        # create completer
        self._completer = CustomCompleter()
        self._completer.setModel(self._model)

        self._line_edit.setCompleter(self._completer)

        # create layout
        self._lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)
        self._lyt.addWidget(self._view)
        self._lyt.addWidget(self._line_edit)

        print self._model.rootPath()


if __name__ == "__main__":
    app = Qt.QtWidgets.QApplication(sys.argv)

    gui = TestWidget()
    gui.show()

    sys.exit(app.exec_())
