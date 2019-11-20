"""Stuff

"""

import sys

import os

try:
    from Qt import QtCore
    from Qt import QtWidgets
    from Qt import QtGui
except ImportError:
    print "[ WARNING ] Cannot find Qt library, using PySide2 instead"
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtGui

# Qt.QtCore.SIGNAL doesn't seem to exist
# TODO investigate why
try:
    from PySide.QtCore import SIGNAL
except ImportError:
    from PySide2.QtCore import SIGNAL


class CollapsableSplitterWidget(QtWidgets.QSplitter):
    def __init__(self, label="", parent=None,):
        super(CollapsableSplitterWidget, self).__init__(parent=parent)

        self._margin = 2

        # self.lyt = QtWidgets.QHBoxLayout()
        # self.setLayout(self.lyt)
        #
        # self._splitter = QtWidgets.QSplitter()

        self.setOrientation(QtCore.Qt.Vertical)
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        self.setLineWidth(1)

        self._label_widget = QtWidgets.QWidget()
        self._label_lyt = QtWidgets.QHBoxLayout()
        self._label_widget.setLayout(self._label_lyt)

        self._expand_btn = QtWidgets.QPushButton("-")
        self._expand_btn.setFixedWidth(15)
        self._expand_btn.setFixedHeight(15)

        self._label = QtWidgets.QLabel(label)
        self._label_lyt.addWidget(self._expand_btn)
        self._label_lyt.addWidget(self._label)
        self._label_lyt.addStretch()

        self._contents_widget = QtWidgets.QWidget()
        self._contents_lyt = QtWidgets.QVBoxLayout()

        self._contents_widget.setLayout(self._contents_lyt)

        self.addWidget(self._label_widget)
        self.addWidget(self._contents_widget)

        # self._scene_tree_widget.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.Maximum)
        # self._object_connections_widget.sizePolicy().setVerticalPolicy(QtWidgets.QSizePolicy.Minimum)

        self.setCollapsible(0, False)
        self.setCollapsible(1, True)

        self.setStretchFactor(1, 1)

        self.setSizes([
            self._label_widget.minimumSizeHint().height(),
            1
        ])

        self.set_margins(self._margin)
        self.connect_widgets()

    def connect_widgets(self):
        self._expand_btn.clicked.connect(self.toggle_collapse)

    def set_margins(self, margin):
        self._margin = margin

        self._label_lyt.setContentsMargins(*[margin] * 4)
        self._contents_lyt.setContentsMargins(*[margin] * 4)

        # refresh sizes
        self.setSizes([
            self._label_widget.minimumSizeHint().height(),
            self._contents_widget.sizeHint().height()
        ])

    def add_widget(self, widget):
        self._contents_lyt.addWidget(widget)

    def collapse(self):
        self.setSizes([
            self._label_widget.minimumSizeHint().height(),
            0
        ])

        self._expand_btn.setText("+")

        self.setFixedHeight(
            self._label_widget.minimumSizeHint().height() + (self._margin * 2)
        )

    def expand(self):
        self.setMaximumHeight(10000)

        self.setSizes([
            self._label_widget.minimumSizeHint().height(),
            self._contents_widget.sizeHint().height()
        ])

        self._expand_btn.setText("-")

        self.resize(
            self.width(),
            self.sizeHint().height()
            # self._label_widget.minimumSizeHint().height() + self._contents_widget.sizeHint().height()
        )


    def toggle_collapse(self):
        if self.sizes()[1] == 0:
            self.expand()
        else:
            self.collapse()


class AdaptiveSplitter(QtWidgets.QSplitter):


    def __init__(self, parent=None):
        super(AdaptiveSplitter, self).__init__(parent=parent)
        self._cached_sizes = []
        self._cached_size_hints = []

    def get_widget_size_hints(self):
        size_hints = []

        for i in range(self.count()):
            widget = self.widget(i)
            size_hint = widget.sizeHint()

            if self.orientation() == QtCore.Qt.Vertical:
                size_hints.append(size_hint.height())
            else:
                size_hints.append(size_hint.width())

        return size_hints


    def get_minimum_height(self):
        sizes = []

        for i in range(self.count()):
            widget = self.widget(i)
            sizes.append(widget.minimumHeight())

        if self.orientation() == QtCore.Qt.Vertical:
            return sum(sizes) + self.total_handle_width()
        else:
            return max(sizes)

    def get_minimum_width(self):
        sizes = []

        for i in range(self.count()):
            widget = self.widget(i)
            sizes.append(widget.minimumWidths())

        if self.orientation() == QtCore.Qt.Horizontal:
            return sum(sizes) + self.total_handle_width()
        else:
            return max(sizes)


    def get_maximum_height(self):
        sizes = []

        for i in range(self.count()):
            widget = self.widget(i)
            sizes.append(widget.maximumHeight())

        if self.orientation() == QtCore.Qt.Vertical:
            return sum(sizes) + self.total_handle_width()
        else:
            return min(sizes)

    def get_maximum_width(self):
        sizes = []

        for i in range(self.count()):
            widget = self.widget(i)
            sizes.append(widget.maximumWidth())

        if self.orientation() == QtCore.Qt.Horizontal:
            return sum(sizes) + self.total_handle_width()
        else:
            return min(sizes)

    def get_widget_minimum_sizes(self):
        sizes = []

        for i in range(self.count()):
            widget = self.widget(i)
            sizes.append(widget.minimumSize())

        return sizes

    def get_widget_maximum_sizes(self):
        sizes = []

        for i in range(self.count()):
            widget = self.widget(i)
            sizes.append(widget.maximumSize())

        return sizes

    def total_handle_width(self):
        return self.handleWidth() * (self.count() - 1 )

    def begin_widget_resize(self):
        print "begin resize"
        self._cached_sizes = list(self.sizes())
        self._cached_size_hints = self.get_widget_size_hints()
        print self._cached_sizes
        print self._cached_size_hints

        # self.setSizes([
        #     self._scene_tree_widget.maximumSize().height(),
        #     self._object_cons_col_widget.minimumSizeHint().height(),
        # ])

    def end_widget_resize(self):
        print "end resize"
        current_sizes = list(self.sizes())
        current_size_hints = self.get_widget_size_hints()

        new_sizes = []

        for i in range(self.count()):
            if current_size_hints[i] != self._cached_size_hints[i]:
                desired_size = current_size_hints[i]
            else:
                desired_size = self._cached_sizes[i]

            new_sizes.append(desired_size)

        size = sum(new_sizes) + self.total_handle_width()
        print "new sizes", new_sizes
        print "sum sizes", size

        if self.orientation() == QtCore.Qt.Vertical:
            self.setMinimumHeight(
                self.get_minimum_height()
            )

            self.setMaximumHeight(
                self.get_maximum_height()
            )

            self.resize(
                self.width(),
                size
            )
        else:
            self.setMinimumWidth(
                self.get_minimum_width()
            )

            self.setMaximumWidth(
                self.get_maximum_width()
            )

            self.resize(
                size,
                self.height()
            )

        self.setSizes(new_sizes)

        print "sizes", self.sizes()
        print "size", self.size()


class CollapsableWidget(QtWidgets.QFrame):
    ABOUT_TO_RESIZE = QtCore.Signal()
    RESIZED = QtCore.Signal()

    def __init__(self, label="", parent=None,):
        super(CollapsableWidget, self).__init__(parent=parent)

        self._collapsed_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_ToolBarHorizontalExtensionButton
        )

        self._expanded_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_ToolBarVerticalExtensionButton
        )

        self._margin = 5
        self._expanded = True

        self._lyt = QtWidgets.QVBoxLayout()
        self._lyt.setContentsMargins(0,0,0,0)
        self._lyt.setSpacing(0)

        self.setLayout(self._lyt)
        #
        # self._splitter = QtWidgets.QSplitter()

        # self.setOrientation(QtCore.Qt.Vertical)
        # self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        # self.setLineWidth(1)

        self._expand_btn = QtWidgets.QPushButton(label)
        self._expand_btn.setIcon(self._expanded_icon)
        self._expand_btn.setStyleSheet("Text-align:left")

        # self._expand_btn.setFixedWidth(20)
        self._expand_btn.setFixedHeight(25)

        # self._label = QtWidgets.QLabel(label)
        # self._label_lyt.addWidget(self._expand_btn)
        # self._label_lyt.addWidget(self._label)
        # self._label_lyt.addStretch()

        self._contents_widget = QtWidgets.QWidget()
        self._contents_lyt = QtWidgets.QVBoxLayout()

        self._contents_widget.setLayout(self._contents_lyt)

        self._lyt.addWidget(self._expand_btn)
        self._lyt.addWidget(self._contents_widget)


        # self.setSizes([
        #     self._label_widget.minimumSizeHint().height(),
        #     1
        # ])

        self.set_margins(self._margin)
        self.connect_widgets()

    def connect_widgets(self):
        self._expand_btn.clicked.connect(self.toggle_collapse)

    def set_margins(self, margin):
        self._margin = margin

        self._contents_lyt.setContentsMargins(*[margin] * 4)

        # refresh sizes
        # self.setSizes([
        #     self._label_widget.minimumSizeHint().height(),
        #     self._contents_widget.sizeHint().height()
        # ])

    def add_widget(self, widget):
        self._contents_lyt.addWidget(widget)

    def collapse(self):
        if not self._expanded:
            return True

        self.ABOUT_TO_RESIZE.emit()

        # self._lyt.removeWidget(self._contents_widget)
        self._contents_widget.setFixedHeight(0)
        self._expand_btn.setIcon(self._collapsed_icon)

        self.setFixedHeight(
            self._expand_btn.minimumSizeHint().height()
        )

        self._expanded = False

        self.RESIZED.emit()

    def expand(self):
        if self._expanded:
            return True

        self.ABOUT_TO_RESIZE.emit()

        # self._lyt.addWidget(self._contents_widget)
        self._contents_widget.setMaximumHeight(100000)
        self.setMaximumHeight(100000)

        self._contents_widget.resize(
            self._contents_widget.width(),
            self._contents_widget.sizeHint().height()
        )

        self.resize(
            self.width(),
            self.sizeHint().height()
            # self._label_widget.minimumSizeHint().height() + self._contents_widget.sizeHint().height()
        )

        self._expand_btn.setIcon(self._expanded_icon)
        self._expanded = True

        self.RESIZED.emit()

    def toggle_collapse(self):
        if self._expanded:
            self.collapse()
        else:
            self.expand()



class Test1(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Test1, self).__init__(parent=parent)

        self.lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self.lyt)

        # self._main_splitter = QtWidgets.QSplitter()
        # self._main_splitter.setOrientation(QtCore.Qt.Vertical)
        # self.lyt.addWidget(self._main_splitter)

        self._widget_1 = CollapsableSplitterWidget(label="test1")
        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._widget_1.add_widget(self._edit_1)

        self._widget_2 = CollapsableSplitterWidget(label="test2")
        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._widget_2.add_widget(self._edit_2)

        self.lyt.addWidget(self._widget_1)
        self.lyt.addWidget(self._widget_2)

        self.lyt.addStretch()

        self.show()

class Test2(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Test2, self).__init__(parent=parent)

        self.lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self.lyt)

        self._splitter = QtWidgets.QSplitter()
        self._splitter.setOrientation(QtCore.Qt.Vertical)
        self._splitter.setChildrenCollapsible(False)

        self.lyt.addWidget(self._splitter)

        self._widget_1 = CollapsableWidget(label="test1")
        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._widget_1.add_widget(self._edit_1)

        self._widget_2 = CollapsableWidget(label="test2")
        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._widget_2.add_widget(self._edit_2)

        # self.lyt.addWidget(self._widget_1)
        # self.lyt.addWidget(self._widget_2)
        self._splitter.addWidget(self._widget_1)
        self._splitter.addWidget(self._widget_2)

        self._splitter_spacer = QtWidgets.QWidget()
        self._splitter.addWidget(self._splitter_spacer)

        self.lyt.addStretch()

        self.show()

class Test0(object):
    def __init__(self):
        self._widget_1 = CollapsableWidget("test")
        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._widget_1.add_widget(self._edit_1)
        self._widget_1.show()

class Test3(object):
    def __init__(self):

        self._splitter = AdaptiveSplitter()
        self._splitter.setOrientation(QtCore.Qt.Vertical)
        self._splitter.setChildrenCollapsible(False)

        self._widget_1 = CollapsableWidget(label="test1")
        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._widget_1.add_widget(self._edit_1)

        self._widget_2 = CollapsableWidget(label="test2")
        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._widget_2.add_widget(self._edit_2)

        # self.lyt.addWidget(self._widget_1)
        # self.lyt.addWidget(self._widget_2)
        self._splitter.addWidget(self._widget_1)
        self._splitter.addWidget(self._widget_2)

        self._splitter.resize(
            400,
            600
        )

        self._splitter.setHandleWidth(100)

        self._splitter.setSizes([400, 200])
        print self._splitter.sizes()

        print self._splitter.size()

        self._widget_1.ABOUT_TO_RESIZE.connect(self._splitter.begin_widget_resize)
        self._widget_1.RESIZED.connect(self._splitter.end_widget_resize)

        self._widget_2.ABOUT_TO_RESIZE.connect(self._splitter.begin_widget_resize)
        self._widget_2.RESIZED.connect(self._splitter.end_widget_resize)

        self._splitter.show()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    if True:
        test = Test3()
        # test.show()

    sys.exit(app.exec_())
