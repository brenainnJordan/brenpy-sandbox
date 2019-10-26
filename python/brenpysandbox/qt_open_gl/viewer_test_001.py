'''
Created on Apr 22, 2017

@author: User
'''

import sys

from Camera import Camera
from PyQt4 import QtGui, QtCore
from PyQt4.QtOpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import OpenGL_accelerate
#from OpenGL.GL import glClearColor, glClearDepth
import time
import numpy
import random

class Viewer3DWidget(QGLWidget):
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

        path = r'C:\Partition\Bren\Projects\3D\Photogrametry\RichmondPark\RichmondParl_Tree3\Tree_003_001.1.ply'
        self.readPly(path)

        self.vertex_shader = """
        #version 330
        in vec4 position;
        in vec4 color;
        void main()
        {
           gl_Position = position;
        }
        """
        
        self.fragment_shader = """
        #version 330
        void main()
        {
           gl_FragColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
        }
        """

        self.setMouseTracking(True)
        # self.setMinimumSize(500, 500)
        self.camera = Camera()
        self.camera.setSceneRadius( 2 )
        self.camera.reset()
        self.isPressed = False
        self.oldx = self.oldy = 0


    def create_object(self):
        # Create a new VAO (Vertex Array Object) and bind it
        vertex_array_object = glGenVertexArrays(1)
        glBindVertexArray( vertex_array_object )

        # Generate buffers to hold our vertices
        vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)

        # Get the position of the 'position' in parameter of our shader and bind it.
        position = glGetAttribLocation(self.shader, 'position')
        #color = glGetAttribLocation(self.shader, 'color')
        #print color

        glEnableVertexAttribArray(position)
        #glEnableVertexAttribArray(color)
        
        # Describe the position data layout in the buffer
        glVertexAttribPointer(position, 4, GL_FLOAT, False, 0, ctypes.c_void_p(0))

        # Send the data over to the buffer
        #points = numpy.random.rand(1000, 3).astype(numpy.float32) * 100.0
        #print len(points)
        glBufferData(GL_ARRAY_BUFFER, len(self.np_verts), self.np_verts, GL_STATIC_DRAW)
        
        # Unbind the VAO first (Important)
        glBindVertexArray( 0 )

        # Unbind other stuff
        glDisableVertexAttribArray(position)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.vertex_array_object = vertex_array_object

    def paintGL(self):
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        self.camera.transform()
        glMatrixMode( GL_MODELVIEW );
        glLoadIdentity();

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDepthFunc( GL_LEQUAL );
        glEnable( GL_DEPTH_TEST );
        glEnable( GL_CULL_FACE );
        glFrontFace( GL_CCW );
        glDisable( GL_LIGHTING );
        glShadeModel( GL_FLAT );

        glPointSize(2.0)
        glColor(0.0, 1.0, 1.0)
        glBindVertexArray( self.vertex_array_object )
        glDrawArrays(GL_POINTS, 0, len(self.np_verts))
    
        '''
        glColor(1.0, 1.0, 1.0)
        glBegin(GL_LINE_STRIP)
        glVertex(-1,-1,-1)
        glVertex( 1,-1,-1)
        glVertex( 1, 1,-1)
        glVertex(-1, 1,-1)
        glVertex(-1,-1, 1)
        glVertex( 1,-1, 1)
        glVertex( 1, 1, 1)
        glVertex(-1, 1, 1)
        glEnd()
        '''
        '''
        glBegin(GL_POINTS)

        start = time.time()

        for vert in self.verts:
            colour = [i/255.0 for i in vert['colour']]
            pos = vert['vert']
            glColor(*colour)
            glVertex(*pos)

        end = time.time()
        duration = end-start
        print duration

        glEnd()
        '''
        # axis
        glColor(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 1, 0, 0)
        glEnd()
        glColor(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 0, 1, 0)
        glEnd()
        glColor(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex( 0, 0, 0)
        glVertex( 0, 0, 1)
        glEnd()

        glFlush()


    def resizeGL(self, widthInPixels, heightInPixels):
        self.camera.setViewportDimensions(widthInPixels, heightInPixels)
        glViewport(0, 0, widthInPixels, heightInPixels)

    def initializeGL(self):
        glClearColor(0.5, 0.5, 0.5, 1.0)
        #glEnable(GL_DEPTH_TEST)
        #glClearDepth(1.0)

        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(self.vertex_shader, GL_VERTEX_SHADER)
            #OpenGL.GL.shaders.compileShader(self.fragment_shader, GL_FRAGMENT_SHADER)
        )

        self.create_object()

    def mouseMoveEvent(self, mouseEvent):
        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton :
            # user is dragging
            delta_x = mouseEvent.x() - self.oldx
            delta_y = self.oldy - mouseEvent.y()
            if int(mouseEvent.buttons()) & QtCore.Qt.LeftButton :
                if int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
                    self.camera.dollyCameraForward( 3*(delta_x+delta_y), False )
                else:
                    self.camera.orbit(self.oldx,self.oldy,mouseEvent.x(),mouseEvent.y())
            elif int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
                self.camera.translateSceneRightAndUp( delta_x, delta_y )
            self.update()
        self.oldx = mouseEvent.x()
        self.oldy = mouseEvent.y()

    def readPly(self, path):
        
        #user options
        outputAppendage = '_002'
        minColour = [0,0,0]
        maxColour = [190,190,190]
        
        #do stuff
        outputPath = '%s%s.ply' %( path[0:len(path)-4], outputAppendage)
        
        print 'Reading PLY...'
        f = open(path, 'r')
        lines = f.readlines()
        #outF = open(outputPath, 'w')
        #outF.write('')
        #outF = open(outputPath, 'a')
        
        header = True
        vc = 0
        
        #stuff to store
        newLines = []
        verts = []
        vert_array = []

        min_t = [0, 0, 0]
        max_t = [0, 0, 0]

        print 'Storing PLY data...'
        for line in lines:
            if header:
                newLines.append(line)
            else:
                l = line.split(' ')
                #vert = [float(l[0]),float(l[1]),float(l[2])]
                #vertNormal = [float(l[3]),float(l[4]),float(l[5])]
                #colour = [float(l[6]),float(l[7]),float(l[8])]
                
                vert = [float(i) for i in l[:3]]
                vertNormal = [float(i) for i in l[3:6]]
                colour = [float(i) for i in l[6:9]]
                #vert_array += vert+[1.0]
                vert_array += vert+[1]#+colour

                verts.append({
                    'vert': vert,
                    'colour': colour,
                })

                if True:
                    min_t = [a if a < b else b for a,b in zip(vert, min_t)]
                    max_t = [a if a > b else b for a,b in zip(vert, max_t)]

                #check colour
                if False:
                    if minColour[0] < colour[0] < maxColour[0] and minColour[1] < colour[1] < maxColour[1] and minColour[2] < colour[2] < maxColour[2]:
                        newLines.append(line)
                        vc += 1
            
            if 'end_header' in line:
                header = False
        
        newLines[3] = 'element vertex %d\n' %vc
        print min_t
        print max_t
        '''
        for line in newLines:
        print 'Writing new PLY...'
            outF.write(line)
        '''
        
        f.close()
        #outF.close()

        np_verts = numpy.array(vert_array, dtype=numpy.float32)
        #print vert_array
        #print np_verts

        print 'Finished reading PLY...'
        self.verts = verts
        self.min_t = min_t
        self.max_t = max_t
        self.vert_array = vert_array
        self.np_verts = np_verts
    

class PythonQtOpenGLDemo(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        viewer3D = Viewer3DWidget(self)
        self.setCentralWidget(viewer3D)
        self.resize(500,500)


if __name__ == '__main__':
    # app = QtGui.QApplication(['Python Qt OpenGL Demo'])
    app = QtGui.QApplication(sys.argv)
    window = PythonQtOpenGLDemo()
    window.show()
    sys.exit(app.exec_())
