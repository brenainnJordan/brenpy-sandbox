import sys
from brenpy.qt.core.bpQtImportUtils import QtCore
from brenpy.qt.core.bpQtImportUtils import QtWidgets
from brenpy.qt.core.bpQtImportUtils import QtGui
from brenpy.qt.widgets import bpQtImgWidgets

TEST_IMG = r"D:\Dev\test_data\dorritoMan.jpg"

def paint_test():
    widget = bpQtImgWidgets.BpImageWidget()

    widget.load_image(TEST_IMG)

    painter = QtGui.QPainter(widget.pixmap())
    pen = QtGui.QPen(QtGui.QColor(255, 0, 0))  # Red color
    pen.setWidth(5)
    painter.setPen(pen)

    # Draw a line
    painter.drawLine(QtCore.QPoint(50, 50), QtCore.QPoint(200, 200))

    # Finish painting
    painter.end()

    return widget


class MouseTest(bpQtImgWidgets.BpImageWidget):
    def __init__(self):
        super(MouseTest, self).__init__()

        self.mouse_pressed = False
        self.painter = QtGui.QPainter()
        self.setMouseTracking(True)

        self.load_image(TEST_IMG)
        self.edited_pixmap = self.pixmap().copy()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.mouse_pressed = event.button() == QtCore.Qt.LeftButton

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):

        if not self.pixmap():
            return

        edit_pixmap = self.edited_pixmap.copy()

        self.painter.begin(edit_pixmap)
        # self.painter = QtGui.QPainter(edit_pixmap)

        pen = QtGui.QPen(QtGui.QColor(255, 0, 0))  # Red color
        pen.setWidth(2)
        self.painter.setPen(pen)

        if self.mouse_pressed:
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0))  # Red color
            pen.setWidth(5)
            self.painter.setPen(pen)

            self.painter.drawPoint(QtCore.QPoint(event.x(), event.y()))

            self.edited_pixmap = edit_pixmap.copy()

        self.painter.drawEllipse(QtCore.QPoint(event.x(), event.y()), 5, 5)

        self.painter.end()

        self.setPixmap(edit_pixmap)

        # print("Mouse Position: ({} {})".format(event.x(), event.y()))

        return



class PointEditTest(bpQtImgWidgets.BpImageWidget):
    def __init__(self):
        super(PointEditTest, self).__init__()

        self.point = (50, 50)

        self.mouse_pressed = False
        self.dragging = False

        self.painter = QtGui.QPainter()
        self.setMouseTracking(True)

        self.load_image(TEST_IMG)
        self.orig_pixmap = self.pixmap().copy()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.mouse_pressed = event.button() == QtCore.Qt.LeftButton

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):

        if not self.pixmap():
            return

        edit_pixmap = self.orig_pixmap.copy()

        self.painter.begin(edit_pixmap)

        point = QtCore.QPoint(*self.point)

        # get distance from mouse to point
        distance = (point - event.pos()).manhattanLength()

        if distance < 5 or self.dragging:
            # move point to mouse position
            if self.mouse_pressed:
                self.dragging = True
                self.point = (event.x(), event.y())
                point = event.pos()
            else:
                self.dragging = False
            
            # draw circle around point
            pen = QtGui.QPen(QtGui.QColor(255, 255, 255))
            pen.setWidth(1)
            self.painter.setPen(pen)
            self.painter.drawEllipse(point, 5, 5)


        # draw point
        pen = QtGui.QPen(QtGui.QColor(255, 0, 0))  # Red color
        pen.setWidth(3)
        self.painter.setPen(pen)
        self.painter.drawEllipse(point, 2, 2)

        # finalize
        self.painter.end()
        self.setPixmap(edit_pixmap)

        return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # widget = paint_test()
    # widget = MouseTest()
    widget = PointEditTest()
    widget.show()

    sys.exit(app.exec_())

