'''
Created on Apr 16, 2017

@author: User
'''

import sys
from PyQt4 import QtGui


class tree_thing(QtGui.QWidget):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(tree_thing, self).__init__()
        
        self.tree = QtGui.QTreeView()
        self.tree.setModel(QtGui.QStandardItemModel())
        self.tree.model().setHorizontalHeaderLabels(['Parameter', 'Value', 'things'])
        self.tree.model().itemChanged.connect(self.item_changed)

        parent = QtGui.QStandardItem('twat')
        self.tree.model().appendRow(parent)

        a = QtGui.QStandardItem('cheese')
        b = QtGui.QStandardItem('biscuit')
        c = QtGui.QStandardItem('234')
        parent.appendRow([a, b, c])


        self.treeA = QtGui.QTreeView()
        self.treeA.setModel(QtGui.QStandardItemModel())
        self.treeA.model().setHorizontalHeaderLabels(['Parameter', 'Value', 'things'])

        parent = QtGui.QStandardItem('twat')
        self.treeA.model().appendRow(parent)

        a = QtGui.QStandardItem('cheese')
        b = QtGui.QStandardItem('biscuit')
        c = QtGui.QStandardItem('234')
        parent.appendRow([a, b, c])

        self.tree.expandAll()

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.tree)
        hbox.addWidget(self.treeA)
        self.setLayout(hbox)
        self.setGeometry(0, 100, 400, 600)

    def item_changed(self, item):
        print item.text()


def show_thing():
    app = QtGui.QApplication(sys.argv)
    thing = tree_thing()
    thing.show()
    app.exec_()
    
show_thing()