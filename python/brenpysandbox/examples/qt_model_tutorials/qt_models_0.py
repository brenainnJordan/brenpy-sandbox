'''
Created on 9 Jun 2018

https://www.youtube.com/watch?v=azGfJ7-wK_g


Simple shared model across views

'''

#from PyQt4 import QtGui
from PySide import QtGui, QtCore
import sys


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")

    # ALL OF OUR VIEWS
    listView = QtGui.QListView()
    listView.show()

    treeView = QtGui.QTreeView()
    treeView.show()

    comboBox = QtGui.QComboBox()
    comboBox.show()

    tableView = QtGui.QTableView()
    tableView.show()

    model = QtGui.QStringListModel([
        "blah",
        "things",
        "stuff",
    ])

    # model.setStringList(data)

    listView.setModel(model)
    comboBox.setModel(model)
    tableView.setModel(model)
    treeView.setModel(model)

    sys.exit(app.exec_())
