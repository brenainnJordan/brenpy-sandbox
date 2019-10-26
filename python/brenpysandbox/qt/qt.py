'''
Created on 4 Feb 2018

@author: Bren

QT sandbox
'''

import sys
from PySide import QtGui, QtCore

# testing QT inheritance

class Test(QtGui.QWidget):
    def __init__(self, parent):
        super(Test, self).__init__(parent)

class Thing(Test):
    def __init__(self, parent):
        super(Thing, self).__init__(parent)

class Window(QtGui.QMainWindow):
    def __init__(self, parent):
        super(Window, self).__init__(parent)
        #thing = Thing(None)
        
        #self.setCentralWidget(QtGui.QWidget())
        self.setCentralWidget(Thing(parent))
        
        self.show()
        
        

app = QtGui.QApplication(sys.argv)
gui = Window(None)
app.exec_()
