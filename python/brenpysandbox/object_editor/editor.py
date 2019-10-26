'''
Created on 13 May 2018

@author: Bren
'''

import sys
import os

from PySide import QtGui, QtCore

# objects ---

class ObjectWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(ObjectWidget, self).__init__(*args, **kwargs)
        self.populate()
    
    def populate(self):
        self._v_lyt = QtGui.QVBoxLayout()
        self._tree = ObjectTree()
        self._v_lyt.addWidget(self._tree)


class ObjectItem(QtGui.QStandardItem):
    def __init__(self, *args, **kwargs):
        super(ObjectItem, self).__init__(*args, **kwargs)

class ObjectTree(QtGui.QTreeView):
    def __init__(self, *args, **kwargs):
        super(ObjectTree, self).__init__(*args, **kwargs)
        
        self._model = QtGui.QStandardItemModel()
        self.setModel(self._model)

# components ---

class ComponentWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(ComponentWidget, self).__init__(*args, **kwargs)

# main GUI ---

class Editor(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)
        
        self.populate()
    
    def populate(self):
        self.resize(800, 500) # is this the best way?
        
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._main_lyt = QtGui.QHBoxLayout()
        self.central_widget.setLayout(self._main_lyt)
        
        self._object_widget = ObjectWidget()
        self._main_lyt.addWidget(self._object_widget)
        
        self._component_layout = None


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Editor()
    window.show()
    sys.exit(app.exec_())
