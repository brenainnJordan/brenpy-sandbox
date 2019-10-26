'''
Created on 1 Aug 2019

@author: Bren


TODO create examples of widget delegates

https://doc.qt.io/qt-5/model-view-programming.html#delegate-classes

https://doc.qt.io/qt-5/qtwidgets-widgets-icons-example.html#

see ImageDelegate class


classes:
https://doc.qt.io/qt-5/qitemdelegate.html
https://doc.qt.io/qt-5/qstyleditemdelegate.html


other examples:
https://doc.qt.io/qt-5/qtwidgets-itemviews-stardelegate-example.html#
https://doc.qt.io/qt-5/qtwidgets-itemviews-pixelator-example.html#
https://doc.qt.io/qt-5/qtwidgets-itemviews-chart-example.html#



TODO 1
- simple spin box example

TODO 2
- combo box list example

TODO 2
- make a list of (some) class instances
- each class contains several bits of editable data
- make a deligate that can read/edit said data

Notes:
in each case we can simply display the listview widget
no need for any other widgets

'''

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


# Test 1 ---


# Test 2 ---


# Test 3 ---


if __name__ == "__main__":
    app = Qt.QtWidgets.QApplication(sys.argv)

    gui = None
    gui.show()

    sys.exit(app.exec_())
