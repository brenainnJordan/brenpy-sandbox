"""
https://doc.qt.io/qt-5/qtwidgets-dialogs-tabdialog-example.html
https://doc.qt.io/qt-5/qtabwidget.html#addTab
"""

import sys

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


class TextWidget(Qt.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TextWidget, self).__init__(parent=parent)

        self.lyt = Qt.QtWidgets.QVBoxLayout()
        self.edit = Qt.QtWidgets.QTextEdit()
        self.setLayout(self.lyt)
        self.lyt.addWidget(self.edit)


class TabExampleWidget(Qt.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TabExampleWidget, self).__init__(parent=parent)

        self._create_widgets()
        self._create_tabs()
        self._create_layout()

    def _create_tabs(self):
        self.tab_widget = Qt.QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)

        self.tab_widget.addTab(self.widget_1, "Tab1")
        self.tab_widget.addTab(self.widget_2, "Tab2")
        self.tab_widget.addTab(self.widget_3, "Tab3")

    def _create_widgets(self):
        self.widget_1 = TextWidget()
        self.widget_2 = TextWidget()
        self.widget_3 = TextWidget()

    def _create_layout(self):
        self.lyt = Qt.QtWidgets.QVBoxLayout()
        self.setLayout(self.lyt)
        self.lyt.addWidget(self.tab_widget)


if __name__ == "__main__":
    app = Qt.QtWidgets.QApplication(sys.argv)

    widget = TabExampleWidget()
    widget.show()

    sys.exit(app.exec_())
