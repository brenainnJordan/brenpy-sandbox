"""DIY splitter using layout and dragable buttons and custom behaviour.

The idea being we can more easily control resize events.

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


class DiySplitterHandle(
    QtWidgets.QPushButton
    # QtWidgets.QLabel
):
    MOUSE_PRESSED = QtCore.Signal(QtWidgets.QWidget)
    MOUSE_RELEASED = QtCore.Signal(QtWidgets.QWidget)
    MOUSE_DRAGGED = QtCore.Signal(QtCore.QPoint)

    def __init__(self, parent=None):
        super(DiySplitterHandle, self).__init__("-----", parent=parent)
        self.setFixedHeight(10)

        self._drag_in_progress = False
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Reimplemented from base class to do stuff.
        """
        res = super(DiySplitterHandle, self).mousePressEvent(event)
        self.MOUSE_PRESSED.emit(self)
        self._drag_in_progress = True
        return res

    def mouseReleaseEvent(self, event):
        """Reimplemented from base class to do stuff.
        """
        res = super(DiySplitterHandle, self).mouseReleaseEvent(event)
        self.MOUSE_RELEASED.emit(self)
        self._drag_in_progress = False
        return res

    def mouseMoveEvent(self, event):
        self._mouse_pos = event.pos()
        # print "moved", self._mouse_pos

        if self._drag_in_progress:
            self.MOUSE_DRAGGED.emit(
                self.mapToGlobal(event.pos())
            )

        # self.repaint()

class DiySplitterOverlay(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(DiySplitterOverlay, self).__init__(parent=parent)

        self.setFrameStyle(self.Panel | self.Plain)

        self._drag_in_progress = False
        self._handle = None
        self._mouse_global_pos = QtCore.QPoint()

        self.setMouseTracking(True)

    def set_handle(self, handle):
        self._handle = handle

    def handle(self):
        return self._handle

    def begin_drag(self):
        print "beginning drag"
        self._drag_in_progress = True
        self.setMouseTracking(True)
        self._mouse_global_pos = self.mapFromGlobal(QtGui.QCursor.pos())

        # self.setFocus(
        #     QtCore.Qt.MouseFocusReason
        # )
        # print "has focus", self.hasFocus()

    def end_drag(self):
        print "ending drag"
        self._drag_in_progress = False
        self.setMouseTracking(False)
        self.repaint()

    def paintEvent(self, event):
        super(DiySplitterOverlay, self).paintEvent(event)

        if self._drag_in_progress or True:
            self.draw_drag_rect()

    # def mouseMoveEvent(self, event):
    #     self._mouse_pos = event.pos()
    #     print "overlay mouse moved", self._mouse_pos
    #     self.repaint()

    def mouse_dragged(self, mouse_global_pos):
        self._mouse_global_pos = self.mapFromGlobal(mouse_global_pos)
        self.repaint()

    # def mousePressEvent(self, event):
    #     """ ** TEMP **
    #     """
    #     res = super(DiySplitterOverlay, self).mousePressEvent(event)
    #     self.begin_drag()
    #     return res
    #
    # def mouseReleaseEvent(self, event):
    #     """ ** TEMP **
    #     """
    #     res = super(DiySplitterOverlay, self).mouseReleaseEvent(event)
    #     self.end_drag()
    #     return res

    def draw_drag_rect(self):

        if self.handle() is None:
            return

        painter = QtGui.QPainter(self)

        global_top_left = self.handle().mapToGlobal(
            self.handle().rect().topLeft()
        )

        # print cursor_pos

        rect = QtCore.QRect(
            self.mapFromGlobal(global_top_left).x(),
            # self.mapFromGlobal(global_top_left).y(),
            self._mouse_global_pos.y() - (self.handle().rect().height() / 2),
            self.handle().rect().width(),
            self.handle().rect().height(),
        )

        # print rect

        # draw outline
        painter.setPen(QtCore.Qt.blue)
        # painter.setPen(QtCore.Qt.DotLine)
        # painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)

        # fill solid colour
        painter.fillRect(
            rect,
            QtGui.QColor(50, 50, 255, a=100)
        )

class DiySplitterWidget(QtWidgets.QWidget):
    def __init__(self, child_widget, height=200, parent=None):
        super(DiySplitterWidget, self).__init__(parent=parent)

        # self.setFixedHeight(height)

        self._lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)

        self._lyt.setContentsMargins(0, 0, 0, 0)
        self._lyt.setSpacing(0)

        self._handle = DiySplitterHandle(parent=self)
        self._lyt.addWidget(child_widget)
        self._lyt.addWidget(self._handle)

        self._child_widget = child_widget

        self.update_fixed_height()

    def handle(self):
        return self._handle

    def set_child_widget(self, child_widget):
        """TODO"""
        pass

    def child_widget(self):
        return self._child_widget

    def update_fixed_height(self):

        fixed_height = sum([
            self._handle.sizeHint().height(), self._child_widget.sizeHint().height()
        ])

        self.setFixedHeight(fixed_height)

    def minimum_height(self):
        return self._handle.sizeHint().height()

class DiySplitter(QtWidgets.QWidget):
    def __init__(self):
        super(DiySplitter, self).__init__()

        self._drag_in_progress = False
        self._active_handle = None

        self._lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self._lyt)
        self._lyt.setContentsMargins(0, 0, 0, 0)
        self._lyt.setSpacing(0)

        self._overlay = DiySplitterOverlay()
        # self._overlay.setEnabled(False)
        # self._overlay.setParent(self)
        self._overlay.setVisible(False)

        self._drag_start_pos = QtCore.QPoint()
        self._drag_end_pos = QtCore.QPoint()
        self._drag_delta_pos = QtCore.QPoint()

        # self.setFixedHeight(200)

    def widget_heights(self):
        widget_heights = []

        for widget in self.widgets():
            widget_heights.append(
                widget.height()
            )

        return widget_heights

    def widget_count(self):
        return self._lyt.count()

    def update_fixed_height(self):
        if self.widget_count() == 0:
            print "Cannot update fixed height when number of widgets is 0"
            return

        fixed_height = sum([
            self._lyt.spacing() * (self.widget_count()-1)
        ] + self.widget_heights())

        self.setFixedHeight(fixed_height)

    def begin_drag(self, handle):
        print "beginning drag"
        # self._overlay = DiySplitterOverlay()
        # self._overlay.setParent(self)
        # self._overlay._active_handle = self._test_handle

        # show overlay
        self._overlay.set_handle(handle)
        self._overlay.setVisible(True)
        self._overlay.begin_drag()

        # cache current mouse position for later
        self._drag_start_pos = self.mapFromGlobal(QtGui.QCursor.pos())

    def end_drag(self, handle):
        print "ending drag"

        # hide overlay
        self._overlay.end_drag()
        self._overlay.setVisible(False)

        # calculate how far the mouse has moved
        self._drag_end_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        self._drag_delta_pos = self._drag_end_pos - self._drag_start_pos

        # print self._drag_delta_pos

        self.apply_drag_delta(handle)

        return True

    def get_handle_index(self, handle):
        splitter_widget = handle.parent()
        handle_index = self._lyt.indexOf(splitter_widget)
        return handle_index

    def apply_drag_delta(self, handle):
        current_height = self.height()

        splitter_widget = handle.parent()

        new_height = splitter_widget.height() + self._drag_delta_pos.y()

        if new_height < splitter_widget.minimum_height():
            new_height = splitter_widget.minimum_height()

        splitter_widget.setFixedHeight(new_height)

        self.update_fixed_height()

        return True

    def items(self):
        widgets = []

        for i in range(self._lyt.count()):
            widgets.append(
                self._lyt.itemAt(i)
            )

        return widgets

    def widgets(self):
        widgets = []

        for i in range(self._lyt.count()):
            widgets.append(
                self._lyt.itemAt(i).widget()
            )

        return widgets

    def add_widget(self, widget):
        self._lyt.addWidget(widget)

        splitter_widget = DiySplitterWidget(widget)

        splitter_widget.handle().MOUSE_PRESSED.connect(
            self.begin_drag
        )

        splitter_widget.handle().MOUSE_RELEASED.connect(
            self.end_drag
        )

        splitter_widget.handle().MOUSE_DRAGGED.connect(
            self._overlay.mouse_dragged
        )

        self._lyt.addWidget(splitter_widget)

        # push overlay back to the top
        self._overlay.setParent(None)
        self._overlay.setParent(self)

        # update height
        self.update_fixed_height()

    def resizeEvent(self, event):
        res = super(DiySplitter, self).resizeEvent(event)
        self._overlay.resize(self.size())
        return res


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = DiySplitter()

    child_1 = QtWidgets.QTextEdit("stuff")

    child_2 = QtWidgets.QTextEdit("stuff")

    widget.add_widget(child_1)
    widget.add_widget(child_2)

    widget.show()

    # does nothing...
    # widget.widgets()[0].resize(200, 500)
    # widget.widgets()[0].setFixedHeight(500)

    # test = widget.items()[0].geometry()
    # test.setHeight(600)
    # widget.items()[0].setGeometry(test)

    sys.exit(app.exec_())
