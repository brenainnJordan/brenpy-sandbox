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

class Test1(object):
    def __init__(self):
        self._widget_1 = SplitterThing()

        self._widget_1.setOrientation(QtCore.Qt.Vertical)
        self._widget_1.setChildrenCollapsible(False)

        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._widget_1.addWidget(self._edit_1)

        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._widget_1.addWidget(self._edit_2)

        self._widget_1.show()

        self._widget_1.splitterMoved.connect(self._splitter_moved)

        self._cached_cursor_pos = None
        self._cached_splitter_pos = None

    def _splitter_moved(self, pos, index):
        cursor_pos = QtGui.QCursor.pos()
        cursor_local_pos = self._widget_1.mapFromGlobal(cursor_pos)

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

        elif cursor_local_pos.y() > self._cached_cursor_pos.y():

            # expansion limited
            delta = cursor_local_pos.y() - self._cached_cursor_pos.y()
            print delta

            # temp cache sizes
            sizes = self._widget_1.sizes()

            # resize
            self._widget_1.resize(
                self._widget_1.width(),
                self._widget_1.height() + delta
            )

            # update sizes
            sizes[index-1] = sizes[index-1] + delta
            self._widget_1.setSizes(sizes)

            self._cached_cursor_pos = cursor_local_pos
            self._cached_splitter_pos = pos + delta
        else:
            self._cached_cursor_pos = cursor_local_pos
            self._cached_splitter_pos = pos

        # print pos, self._widget_1.sizes(), cursor_local_pos, self._widget_1.handleWidth()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    test = Test1()

    sys.exit(app.exec_())
