'''
Created on 6 Jun 2018

@author: Bren
'''


"""
https://www.tutorialspoint.com/pyqt/pyqt_drag_and_drop.htm
"""

import sys
from PySide import QtGui, QtCore


class combo(QtGui.QComboBox):

    def __init__(self, title, parent):
        super(combo, self).__init__(parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        print e

        data = e.mimeData()

        print data

        if data.hasText() or True:
            e.accept()
            print "text : ", data.text()
        else:
            e.ignore()

    def dropEvent(self, e):
        print e.mimeData().text()
        self.addItem(e.mimeData().text())


class StandardItem(QtGui.QStandardItem):

    def __init__(self, *args, **kwargs):
        super(StandardItem, self).__init__(*args, **kwargs)

    def mouseMoveEvent(self, e):
        print "test"
        if e.buttons() != QtCore.Qt.MidButton:
            return

        mimeData = QtCore.QMimeData()

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())

        dropAction = drag.start(QtCore.Qt.MoveAction)

    def mousePressEvent(self, e):
        print "stuff"
        super(StandardItem, self).mousePressEvent(e)

        if e.button() == QtCore.Qt.LeftButton:
            print 'press'


class DragTree(QtGui.QTreeView):
    def __init__(self, *args, **kwargs):
        super(DragTree, self).__init__(*args, **kwargs)

        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        self.drag_start_position = None

    def startDrag(self, drop_actions):
        """
        The DropActions type is a typedef for QFlags<DropAction>.
        It stores an OR combination of DropAction values.

        https://doc.qt.io/archives/qt-4.8/qt.html#DropAction-enum
        """

        if False:
            # debug drop actions
            print "startDrag ", drop_actions, int(drop_actions)

            for action in [
                QtCore.Qt.DropAction.ActionMask,
                QtCore.Qt.DropAction.CopyAction,
                QtCore.Qt.DropAction.IgnoreAction,
                QtCore.Qt.DropAction.LinkAction,
                QtCore.Qt.DropAction.MoveAction,
                QtCore.Qt.DropAction.TargetMoveAction,
            ]:
                print action, int(action)
    #             if action in drop_actions:
    #                 print "action ", action

            # True
            print drop_actions == QtCore.Qt.DropAction.CopyAction | QtCore.Qt.DropAction.MoveAction

            # False
            print drop_actions == QtCore.Qt.DropAction.CopyAction | QtCore.Qt.DropAction.MoveAction | QtCore.Qt.DropAction.LinkAction

        # we can't do this...
#         index = self.indexAt(event.pos())
#         selected = self.model().data(index, QtCore.Qt.UserRole)
#         print index, selected

        # call superclass
        # returns None
        res = QtGui.QTreeView.startDrag(self, drop_actions)
#         print "startDrag: {}".format(res)

        return res

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() != QtCore.Qt.NoButton:

            self.drag_start_position = mouse_event.pos()

            if mouse_event.button() == QtCore.Qt.LeftButton:
                print "left button clicked"

            elif mouse_event.button() == QtCore.Qt.RightButton:
                print "right button clicked"
            elif mouse_event.button() == QtCore.Qt.MidButton:
                print "mid button clicked"
            else:
                print "something else clicked"
        else:
            print " no click? "
            pass

        # call superclass
        return QtGui.QTreeView.mousePressEvent(self, mouse_event)

    def mouseMoveEvent(self, mouse_event):

        if mouse_event.button() == QtCore.Qt.NoButton:
            print "dragging"

            # check drag distance
            # manhattanLength is a fast way to tell how far the mouse has moved
            # at the cost of accuracy
            if self.drag_start_position is not None:
                if (
                    mouse_event.pos() - self.drag_start_position
                ).manhattanLength() < QtGui.QApplication.startDragDistance():
                    print "drag below threshold"
#                     return

            else:
                # error?
                pass

            if mouse_event.buttons() == QtCore.Qt.LeftButton:
                print "left button"

            elif mouse_event.buttons() == QtCore.Qt.RightButton:
                print "right button"
            elif mouse_event.buttons() == QtCore.Qt.MidButton:
                print "mid button"
            elif mouse_event.buttons() == QtCore.Qt.LeftButton | QtCore.Qt.RightButton:
                print "left + right buttons"
            else:
                print "something else"
        else:
            # not dragging?
            pass

        # call superclass
        return QtGui.QTreeView.mouseMoveEvent(self, mouse_event)
#
#         QDrag *drag = new QDrag(this);
#         QMimeData *mimeData = new QMimeData;
#
#         mimeData->setData(mimeType, data);
#         drag->setMimeData(mimeData);
#
# Qt::DropAction dropAction = drag->exec(Qt::CopyAction | Qt::MoveAction);

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() != QtCore.Qt.NoButton:

            self.drag_start_position = None

            if mouse_event.button() == QtCore.Qt.LeftButton:
                print "left button released"

            elif mouse_event.button() == QtCore.Qt.RightButton:
                print "right button released"
            elif mouse_event.button() == QtCore.Qt.MidButton:
                print "mid button released"
            else:
                print "something else released"
        else:
            print " no releas? "
            pass

        # call superclass
        return QtGui.QTreeView.mouseReleaseEvent(self, mouse_event)


class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self):
        QtCore.QAbstractItemModel.__init__(self)
        self.nodes = ['node0', 'node1', 'node2', 'poop']

    def index(self, row, column, parent):
        return self.createIndex(row, column, self.nodes[row])

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, index):
        if index.internalPointer() in self.nodes:
            return 0
        return len(self.nodes)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        if role == 0:
            return index.internalPointer()
        else:
            return None

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def mimeTypes(self):
        #         return ['text/xml']
        return ['text']

    def mimeData(self, indexes):
        print "mimeData()", indexes
        mimedata = QtCore.QMimeData()
#         mimedata.setData('text/xml', 'mimeData')
        text_list = [i.internalPointer() for i in indexes]
        text = ";".join(text_list)

        mimedata.setText(text)

        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        print 'dropMimeData %s %s %s %s' % (data.data('text/xml'), action, row, parent)
        return True


class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):
        lo = QtGui.QFormLayout()
        lo.addRow(QtGui.QLabel(
            "Type some text in textbox and drag it into combo box"))

        edit = QtGui.QLineEdit()
        edit.setDragEnabled(True)

#         self.tree = QtGui.QTreeView()
        self.tree = DragTree()
        # self.tree.setDragEnabled(True)

        self.tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

#         self.model = QtGui.QStandardItemModel()
        self.model = TreeModel()
        # self.model.setSupportedDragActions(QtCore.Qt.MoveAction)
        self.tree.setModel(self.model)
#
#         item1 = QtGui.QStandardItem("test")
#         #item1 = StandardItem("test")
#         item1.setDragEnabled(True)

#         self.model.appendRow(item1)

        com = combo("Button", self)
        lo.addRow(edit, com)

        lo.addRow(self.tree)

        self.setLayout(lo)
        self.setWindowTitle('Simple drag & drop')


def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
