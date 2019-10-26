'''
Created on Jul 16, 2017

@author: Brenainn Jordan

'''

import sys
import inspect

from PySide import QtGui, QtCore
from PySide.QtOpenGL import QGLWidget, QGLFormat

from OpenGL import GL 
#from OpenGL.GLU import *
#from OpenGL.GLUT import *
from OpenGL.GL import shaders

import numpy

from cg.camera import camera
from viewer import ViewerWidget, OpenGlVerts
from utils.utils import args_to_dict


def triangle_data():
    vertex_data = numpy.array([0.75, 0.75, 0.0,
                               0.75, -0.75, 0.0,
                               -0.75, -0.75, 0.0], dtype=numpy.float32)
    
    color_data = numpy.array([1.0, 1.0, 0.0, 1.0,
                              0.0, 1.0, 0.0, 1.0,
                              0.0, 0.0, 1.0, 1.0], dtype=numpy.float32)
    
    color_data = [0.5]*3+[1]
    color_data *= 4
    color_data = numpy.array(color_data, dtype=numpy.float32)
    
    return vertex_data, color_data


def random_color_data(count):
    '''
    Returns random VBO color data
    '''
    
    color_data = numpy.random.rand(count, 4)
    color_data = numpy.ndarray.flatten(color_data)
    color_data = numpy.array(color_data, dtype=numpy.float32)
    return color_data


def square_data():
    verts = [
        [1, 1, 0],
        [-1, 1, 0],
        [-1, -1, 0],
        [1, -1, 0]
    ]
    
    triangles = [
        [0, 1, 2],
        [0, 2, 3]
    ]
    
    triangle_verts = [verts[vert] for triangle in triangles for vert in triangle]
    
    verts = numpy.array(triangle_verts, dtype=numpy.float32)
    verts = numpy.ndarray.flatten(verts)
    
    return verts, random_color_data(len(triangle_verts))


def cube_data():
    verts = [
        [1, 1, 1],
        [-1, 1, 1],
        [-1, -1, 1],
        [1, -1, 1],
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, -1],
        [1, -1, -1]
    ]
    
    triangles = [
        [0, 1, 2],#front1
        [2, 3, 0],#front2
        [0, 4, 7],#lside1
        [7, 3, 0],#lside2
        [0, 1, 5],#top1
        [5, 0, 4],#top2
        [7, 3, 6],#bottom1
        [6, 3, 2],#bottom2
        [6, 5, 4],#back1
        [4, 7, 6],#back2
        [6, 2, 5],#rside1
        [5, 2, 1],#rside2
    ]
    
    triangle_verts = [verts[vert] for triangle in triangles for vert in triangle]
    
    verts = numpy.array(triangle_verts, dtype=numpy.float32)
    verts = numpy.ndarray.flatten(verts)
    
    return verts, random_color_data(len(triangle_verts))


class RandomData(object):
    '''
    generates random 3D points
    '''
    
    def __init__(self):
        self.count = 100
        
        options = {
            'rand': '{}, 3',
            'gamma': '2., 1., {}*3',
            'standard_cauchy': 'size={}*3',
            'rayleigh': 'size={}*3',
            'geometric': '0.35, size={}*3' 
            }
        
        self.options = options
    
    def get_data(self, option):
        args = self.options[option].format(self.count)
        cmd = 'numpy.random.{}({})'.format(option, args)
        return eval(cmd)
    

def random_data_to_vertex_data(positions):
    '''
    Takes random generated position data and converts it into a form readable by openGl
    :positions array, 3 x n numpy array or flat list
    :returns numpy_array, numpy_array
    '''

    vertex_data = numpy.ndarray.flatten(positions)
    vertex_data = numpy.array(vertex_data, dtype=numpy.float32)
    
    count = len(vertex_data)/3
    column_4 = numpy.ndarray([count, 1])
    column_4.fill(1)
    
    color_data = numpy.random.rand(count, 4)
    #color_data = numpy.concatenate((color_data, column_4), axis=1)
    color_data = numpy.ndarray.flatten(color_data)
    color_data = numpy.array(color_data, dtype=numpy.float32)
    
    return vertex_data, color_data


class ViewerWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.debug = True
        
        self.get_verts()
        self.viewer = ViewerWidget(self.verts)
        self.gl_options = args_to_dict(self.viewer.set_options)
        
        self.widget = QtGui.QWidget()
        self.lyt = QtGui.QVBoxLayout()
        self.widget.setLayout(self.lyt)
        self.setCentralWidget(self.widget)
        self.resize(500,500)
        
        #self.get_options()
        self.add_elements()

    
    def get_verts(self):
        self.random_data = RandomData()
        self.random_options = self.random_data.options.keys()
        
        #vertex_data, color_data = triangle_data()
        #vertex_data, color_data = square_data()
        vertex_data, color_data = cube_data()
        
        #raw_data = self.random_data.get_data(self.random_options[0])
        #vertex_data, color_data = random_data_to_vertex_data(raw_data) 
        self.vertex_data = vertex_data
        self.color_data = color_data
        
        self.verts = OpenGlVerts(vertex_data, color_data)
        self.vert_options = args_to_dict(self.verts.draw)
    
    
    def add_options(self, options, name):
        option_lyt = QtGui.QVBoxLayout()
        option_lyt.addStretch()
        
        label = QtGui.QLabel()
        label.setText(name+'\n----------')
        option_lyt.addWidget(label)
        
        for name in sorted(options.keys()):
            value = options[name]
            
            if type(value) == bool:
                check = QtGui.QCheckBox()
                check.setText(name)
                check.setChecked(value)
                check.stateChanged.connect(lambda x,
                                           check=check,
                                           options=options:
                                           self.change_bool_option(check, options))
                
                option_lyt.addWidget(check)
            elif type(value) == int or type(value) == float:
                spin_lyt = QtGui.QHBoxLayout()

                label = QtGui.QLabel()
                label.setText(name)
                
                if type(value) == int:
                    spin = QtGui.QSpinBox()
                else:
                    spin = QtGui.QDoubleSpinBox()
                
                spin.setValue(value)
                spin.valueChanged.connect(lambda x,
                                          label=label,
                                          spin=spin,
                                          options=options:
                                          self.change_numeric_option(label, spin, options))

                spin_lyt.addWidget(spin)                
                spin_lyt.addWidget(label)
                option_lyt.addLayout(spin_lyt)
    
        return option_lyt
    
    
    def add_elements(self):
        h_lyt = QtGui.QHBoxLayout()
        h_lyt.addWidget(self.viewer)
        
        option_lyt = QtGui.QVBoxLayout()
        option_lyt.addStretch()
        
        gl_option_lyt = self.add_options(self.gl_options, 'openGL options')
        option_lyt.addLayout(gl_option_lyt)
        
        vert_option_lyt = self.add_options(self.vert_options, 'Vert rendering')
        option_lyt.addLayout(vert_option_lyt)
        
        h_lyt.addLayout(option_lyt)
        
        h_lyt.setStretch(0, 1)
        self.lyt.addLayout(h_lyt)
        
        combo = QtGui.QComboBox()
        self.combo = combo
        combo.addItems(self.random_options)
        combo.currentIndexChanged.connect(self.update_data)
        self.lyt.addWidget(combo)

    
    def change_bool_option(self, check, options):
        option = check.text()
        value = check.isChecked()
        options[option] = value
        self.update_options()
    
    
    def change_numeric_option(self, label, spin, options):
        option = label.text()
        value = spin.value()
        options[option] = value
        self.update_options()
    
    
    def update_options(self):
        self.viewer.vert_options = self.vert_options
        self.viewer.gl_options = self.gl_options
        self.viewer.update()
        if self.debug:
            print self.vert_options
            print self.gl_options
    
    
    def update_data(self):    
        option = self.combo.currentText()
        print option
        raw_data = self.random_data.get_data(option)
        vertex_data, color_data = random_data_to_vertex_data(raw_data)
        self.verts.set_data(vertex_data, color_data)
        self.verts.bind_data()
        # update viewer
        self.viewer.update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = ViewerWindow()
    window.show()
    sys.exit(app.exec_())
