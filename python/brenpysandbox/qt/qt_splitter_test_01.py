"""Auto expanding splitter * WIP *
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

class SplitterThing(QtWidgets.QSplitter):
    def __init__(self, *args, **kwargs):
        super(SplitterThing, self).__init__(*args, **kwargs)

        self.splitterMoved.connect(self._splitter_moved)

        self._cached_cursor_pos = None
        self._cached_splitter_pos = None

    def _splitter_moved(self, pos, index):
        cursor_pos = QtGui.QCursor.pos()
        cursor_local_pos = self.mapFromGlobal(cursor_pos)

        print pos, cursor_local_pos, self.handleWidth()

        if self._cached_cursor_pos is None:
            self._cached_cursor_pos = cursor_local_pos
            self._cached_splitter_pos = pos
            return

        if pos != self._cached_splitter_pos:
            # splitter moving normally
            self._cached_splitter_pos = pos
            self._cached_cursor_pos = cursor_local_pos
            return

        if cursor_local_pos.y() == self._cached_cursor_pos.y():
            return

        elif all([
            cursor_local_pos.y() > self._cached_cursor_pos.y(),
            cursor_local_pos.y() > pos + self.handleWidth()
        ]):

            # expansion limited
            delta = cursor_local_pos.y() - self._cached_cursor_pos.y()

            # temp cache sizes
            sizes = self.sizes()

            # resize
            self.resize(
                self.width(),
                self.height() + delta
            )

            # update sizes
            sizes[index-1] = sizes[index-1] + delta
            self.setSizes(sizes)

            self._cached_cursor_pos = cursor_local_pos
            self._cached_splitter_pos = pos + delta

        elif all([
            cursor_local_pos.y() < self._cached_cursor_pos.y(),
            cursor_local_pos.y() < pos # - self.handleWidth()
        ]):

            # expansion limited
            delta = cursor_local_pos.y() - self._cached_cursor_pos.y()

            # temp cache sizes
            # sizes = self.sizes()

            # resize
            self.resize(
                self.width(),
                self.height() + delta
            )

            # update sizes
            # sizes[index-1] = sizes[index-1] + delta
            # self.setSizes(sizes)

            self._cached_cursor_pos = cursor_local_pos
            self._cached_splitter_pos = pos + delta

        else:
            self._cached_cursor_pos = cursor_local_pos
            self._cached_splitter_pos = pos

class Test1(object):
    def __init__(self):
        self._widget_1 = SplitterThing()

        self._widget_1.setOrientation(QtCore.Qt.Vertical)
        self._widget_1.setChildrenCollapsible(False)
        self._widget_1.setHandleWidth(50)

        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._edit_3 = QtWidgets.QTextEdit("stuff\nthings3")

        self._btn_1 = QtWidgets.QPushButton("btn 1")
        self._btn_1.setFixedHeight(50)
        self._btn_2 = QtWidgets.QPushButton("btn 2")
        self._btn_2.setFixedHeight(50)
        self._btn_3 = QtWidgets.QPushButton("btn 3")
        self._btn_3.setFixedHeight(50)
        self._btn_4 = QtWidgets.QPushButton("btn 4")
        self._btn_4.setFixedHeight(50)

        self._widget_1.addWidget(self._edit_1)
        self._widget_1.addWidget(self._btn_1)
        self._widget_1.addWidget(self._edit_2)
        self._widget_1.addWidget(self._btn_2)
        self._widget_1.addWidget(self._edit_3)
        self._widget_1.addWidget(self._btn_3)
        self._widget_1.addWidget(self._btn_4)

        self._widget_1.show()

        # print pos, self._widget_1.sizes(), cursor_local_pos, self._widget_1.handleWidth()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    test = Test1()

    sys.exit(app.exec_())
