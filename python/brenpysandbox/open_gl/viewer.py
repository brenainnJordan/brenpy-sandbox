'''
Created on Jul 16, 2017

@author: Brenainn Jordan

help from modern_opengl_01_triangle.py

:todo add min value for point size

python -m pip install PyOpenGL PyOpenGL_accelerate


'''

import sys

from PySide import QtGui, QtCore
from PySide.QtOpenGL import QGLWidget, QGLFormat

from OpenGL import GL
#from OpenGL.GLU import *
#from OpenGL.GLUT import *
from OpenGL.GL import shaders

import numpy

from cg.camera import camera
from utils.utils import args_to_dict


def random_data_to_vertex_data(positions):
    '''
    Takes random generated position data and converts it into a form readable by openGl
    :positions array, 3 x n numpy array or flat list
    :returns numpy_array, numpy_array
    '''

    vertex_data = numpy.ndarray.flatten(positions)
    vertex_data = numpy.array(vertex_data, dtype=numpy.float32)

    count = len(vertex_data) / 3
    column_4 = numpy.ndarray([count, 1])
    column_4.fill(1)

    color_data = numpy.random.rand(count, 4)
    #color_data = numpy.concatenate((color_data, column_4), axis=1)
    color_data = numpy.ndarray.flatten(color_data)
    color_data = numpy.array(color_data, dtype=numpy.float32)

    return vertex_data, color_data


class ShaderProgram(object):
    '''
    Helper class for using GLSL shader programs
    from modern_opengl_01_triangle.py
    '''

    def __init__(self, vertex, fragment):
        '''
        :vertex String containing shader source code for the vertex shader
        :fragment String containing shader source code for the fragment shader
        '''

        if False:
            # method 1
            self.program_id = GL.glCreateProgram()
            vs_id = self.add_shader(vertex, GL.GL_VERTEX_SHADER)
            frag_id = self.add_shader(fragment, GL.GL_FRAGMENT_SHADER)

            GL.glAttachShader(self.program_id, vs_id)
            GL.glAttachShader(self.program_id, frag_id)
            GL.glLinkProgram(self.program_id)

            if GL.glGetProgramiv(self.program_id, GL.GL_LINK_STATUS) != GL.GL_TRUE:
                info = GL.glGetProgramInfoLog(self.program_id)
                GL.glDeleteProgram(self.program_id)
                GL.glDeleteShader(vs_id)
                GL.glDeleteShader(frag_id)
                raise RuntimeError('Error linking program: %s' % (info))
            GL.glDeleteShader(vs_id)
            GL.glDeleteShader(frag_id)

        else:
            # method 2
            vertex_shader = shaders.compileShader(vertex, GL.GL_VERTEX_SHADER)
            fragment_shader = shaders.compileShader(
                fragment, GL.GL_FRAGMENT_SHADER)
            self.program_id = shaders.compileProgram(
                vertex_shader, fragment_shader)

    def add_shader(self, source, shader_type):
        '''
        Helper function for compiling a GLSL shader
        :source String containing shader source code
        :shader_type (valid OpenGL shader type) Type of shader to compile
        :return (int) Identifier for shader if compilation is successful
        '''

        try:
            shader_id = GL.glCreateShader(shader_type)
            GL.glShaderSource(shader_id, source)
            GL.glCompileShader(shader_id)
            if GL.glGetShaderiv(shader_id, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
                info = GL.glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            GL.glDeleteShader(shader_id)
            raise

    def uniform_location(self, name):
        '''
        Helper function to get location of an OpenGL uniform variable
        :name Name of the variable for which location is to be returned
        :return Integer describing location
        '''

        return GL.glGetUniformLocation(self.program_id, name)

    def attribute_location(self, name):
        '''
        Helper function to get location of an OpenGL attribute variable
        :name Name of the variable for which location is to be returned
        :return Integer describing location
        '''

        return GL.glGetAttribLocation(self.program_id, name)


def draw_axes():
    # axis
    GL.glColor(1.0, 0.0, 0.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex(0, 0, 0)
    GL.glVertex(1, 0, 0)
    GL.glEnd()
    GL.glColor(0.0, 1.0, 0.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex(0, 0, 0)
    GL.glVertex(0, 1, 0)
    GL.glEnd()
    GL.glColor(0.0, 0.0, 1.0)
    GL.glBegin(GL.GL_LINES)
    GL.glVertex(0, 0, 0)
    GL.glVertex(0, 0, 1)
    GL.glEnd()
    GL.glFlush()


def draw_grid(xn, zn, xw, zw):
    GL.glColor(0.0, 0.0, 0.0)

    x_max = (xn / 2) * xw
    z_max = (zn / 2) * zw

    x_min = x_max * -1
    z_min = z_max * -1

    # draw lines parallel with z
    for x in range(xn + 1):
        x = x_min + (x * xw)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex(x, 0, z_min)
        GL.glVertex(x, 0, z_max)
        GL.glEnd()

    # draw lines parallel with x
    for z in range(zn + 1):
        z = z_min + (z * zw)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex(x_min, 0, z)
        GL.glVertex(x_max, 0, z)
        GL.glEnd()


class OpenGlVerts(object):
    '''
    class for storing and drawing vertices
    '''

    def __init__(self, vertex_data, color_data):
        self.set_data(vertex_data, color_data)
        self.get_shader_code_v330()

    def set_data(self, vertex_data, color_data):
        self.vertex_data = vertex_data
        self.color_data = color_data
        self.vert_count = len(vertex_data) / 3

    def get_shader_code_v120(self):
        '''
        version 120 allows us to use the gl_ModelViewProjectionMatrix variable
        which allows us to move the camera
        '''

        self.vertex = """
        #version 120
        in vec3 vin_position;
        in vec3 vin_color;
        out vec3 vout_color;
        
        void main(void)
        {
            vout_color = vin_color;
            gl_Position = gl_ModelViewProjectionMatrix * vec4(vin_position, 1.0);
        }
        """

        self.fragment = """
        #version 120
        in vec3 vout_color;
        out vec4 fout_color;
        
        void main(void)
        {
            fout_color = vec4(vout_color, 1.0);
        }
        """

    def get_shader_code_v330(self):
        '''
        TODO replace gl_ModelViewProjectionMatrix variable
        which allows us to move the camera
        '''

        self.vertex = """
        #version 330
        in vec3 vin_position;
        in vec3 vin_color;
        out vec3 vout_color;
        
        void main(void)
        {
            vout_color = vin_color;
            gl_Position = vec4(vin_position, 1.0);
        }
        """

        self.fragment = """
        #version 330
        in vec3 vout_color;
        out vec4 fout_color;
        
        void main(void)
        {
            fout_color = vec4(vout_color, 1.0);
        }
        """

    def create_vbo(self):
        print 'creating vbo'
        # Lets compile our shaders since the use of shaders is now
        # mandatory. We need at least a vertex and fragment shader
        # begore we can draw anything
        program = ShaderProgram(fragment=self.fragment, vertex=self.vertex)

        # Lets create a VAO and bind it
        # Think of VAO's as object that encapsulate buffer state
        # Using a VAO enables you to cut down on calls in your draw
        # loop which generally makes things run faster
        vao_id = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_id)

        # Lets create our Vertex Buffer objects - these are the buffers
        # that will contain our per vertex data
        vbo_id = GL.glGenBuffers(2)

        self.program = program
        self.vao_id = vao_id
        self.vbo_id = vbo_id
        print vao_id
        print vbo_id

    def bind_data(self):
        print 'binding data'
        print self.vao_id
        print self.vbo_id

        # Bind a buffer before we can use it
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo_id[0])

        # Now go ahead and fill this bound buffer with some data
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        GL.ArrayDatatype.arrayByteCount(self.vertex_data),
                        self.vertex_data,
                        GL.GL_STATIC_DRAW)

        # Now specify how the shader program will be receiving this data
        # In this case the data from this buffer will be available in the
        # shader as the vin_position vertex attribute
        GL.glVertexAttribPointer(self.program.attribute_location('vin_position'),
                                 3,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)

        # Turn on this vertex attribute in the shader
        GL.glEnableVertexAttribArray(0)

        # Now do the same for the other vertex buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo_id[1])

        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        GL.ArrayDatatype.arrayByteCount(self.color_data),
                        self.color_data,
                        GL.GL_STATIC_DRAW)

        GL.glVertexAttribPointer(self.program.attribute_location('vin_color'),
                                 4,
                                 GL.GL_FLOAT,
                                 GL.GL_FALSE,
                                 0,
                                 None)

        GL.glEnableVertexAttribArray(1)

        # Lets unbind our vbo and vao state
        # We will bind these again in the draw loop
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def draw(self,
             points=True,
             point_size=10.0,
             lines=True,
             triangles=True,
             test=12
             ):

        program = self.program.program_id
        GL.glUseProgram(program)

        # Bind VAO - this will automatically
        # bind all the vbo's saving us a bunch
        # of calls
        GL.glBindVertexArray(self.vao_id)

        # Modern GL makes the draw call really simple
        # All the complexity has been pushed elsewhere
        if triangles:
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vert_count)
        if lines:
            GL.glDrawArrays(GL.GL_LINE_STRIP, 0, self.vert_count)
        if points:
            GL.glPointSize(point_size)
            GL.glDrawArrays(GL.GL_POINTS, 0, self.vert_count)

        # Lets unbind the shader and vertex array state
        GL.glUseProgram(0)
        GL.glBindVertexArray(0)


class ViewerWidget(QGLWidget):

    def __init__(self, verts_object):
        self.verts = verts_object
        self.vert_options = args_to_dict(self.verts.draw)
        self.gl_options = args_to_dict(self.set_options)

        fmt = QGLFormat()
        fmt.setRgba(True)
        fmt.setDoubleBuffer(False)
        QGLWidget.__init__(self, fmt)
        self.glInit()

        self.setMouseTracking(True)

        self.camera = camera()
        self.camera.setSceneRadius(2)
        self.camera.reset()
        self.isPressed = False
        self.oldx = self.oldy = 0

    def initializeGL(self):
        '''
        set bg color, create vbo and bind to GPU
        '''

        print 'initializing'

        # glEnable(GL_DEPTH_TEST)
        GL.glViewport(0, 0, 1400, 800)
        GL.glClearColor(0.5, 0.5, 0.5, 0)

        self.verts.create_vbo()
        self.verts.bind_data()

    def set_options(self,
                    projection=True,
                    modelView=True,
                    loadIdentity=True,
                    depthFunc=True,
                    depthTest=True,
                    cullFace=False,
                    blend=False,
                    dither=False,
                    clear=True,
                    frontFace=False,
                    lighting=False,
                    smooth=False,
                    show_verts=True,
                    show_grid=True,
                    show_axes=True):

        self.show_verts = show_verts
        self.show_grid = show_grid
        self.show_axes = show_axes

        # glEnableClientState(GL_VERTEX_ARRAY)
        # glEnableClientState(GL_COLOR_ARRAY)

        if projection:
            GL.glMatrixMode(GL.GL_PROJECTION)
        if modelView:
            GL.glMatrixMode(GL.GL_MODELVIEW)
        if loadIdentity:
            GL.glLoadIdentity()

        #glMatrixMode( GL_COLOR )
        if clear:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if depthFunc:
            GL.glDepthFunc(GL.GL_LEQUAL)

        if depthTest:
            GL.glEnable(GL.GL_DEPTH_TEST)
        else:
            GL.glDisable(GL.GL_DEPTH_TEST)

        if cullFace:
            GL.glEnable(GL.GL_CULL_FACE)
        else:
            GL.glDisable(GL.GL_CULL_FACE)

        #glBlendFunc(GL_ONE, GL_ZERO)
        #glBlendFunc(GL_DST_COLOR, GL_SRC_COLOR)
        if blend:
            GL.glEnable(GL.GL_BLEND)
        else:
            GL.glDisable(GL.GL_BLEND)

        if dither:
            GL.glEnable(GL.GL_DITHER)
        else:
            GL.glDisable(GL.GL_DITHER)

        if frontFace:
            GL.glFrontFace(GL.GL_CCW)
        if lighting:
            GL.glEnable(GL.GL_LIGHTING)
            light_ambient = [0.0, 0.0, 0.0, 1.0]
            light_diffuse = [1.0, 1.0, 1.0, 1.0]
            light_specular = [1.0, 1.0, 1.0, 1.0]
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, light_ambient)
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, light_diffuse)
            GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, light_specular)
        else:
            GL.glDisable(GL.GL_LIGHTING)

        if smooth:
            GL.glShadeModel(GL.GL_SMOOTH)
        else:
            GL.glShadeModel(GL.GL_FLAT)

        # glClear(GL_COLOR_BUFFER_BIT)

    def paintGL(self):
        '''
        draw all the things, called by QGLWidget
        '''

        self.set_options(**self.gl_options)

        # move camera
        self.camera.transform()

        # draw points
        if self.show_verts:
            self.verts.draw(**self.vert_options)

        # draw axes and grid
        if self.show_grid:
            draw_grid(10, 10, 1, 1)
        if self.show_axes:
            draw_axes()

    def resizeGL(self, widthInPixels, heightInPixels):
        '''
        detect if window has been resized, and adjust camera setting
        called by QGLWidget
        '''

        self.camera.setViewportDimensions(widthInPixels, heightInPixels)
        GL.glViewport(0, 0, widthInPixels, heightInPixels)

    def mouseMoveEvent(self, mouseEvent):
        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton:
            # user is dragging
            delta_x = mouseEvent.x() - self.oldx
            delta_y = self.oldy - mouseEvent.y()
            if int(mouseEvent.buttons()) & QtCore.Qt.LeftButton:
                self.camera.orbit(self.oldx, self.oldy,
                                  mouseEvent.x(), mouseEvent.y())
            elif int(mouseEvent.buttons()) & QtCore.Qt.MidButton:
                self.camera.translateSceneRightAndUp(delta_x, delta_y)
            elif int(mouseEvent.buttons()) & QtCore.Qt.RightButton:
                self.camera.dollyCameraForward(3 * (delta_x + delta_y), False)
            self.update()
        self.oldx = mouseEvent.x()
        self.oldy = mouseEvent.y()


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
        self.resize(500, 500)

        # self.get_options()
        self.add_elements()

    def get_verts(self):
        return

        vertex_data, color_data = random_data_to_vertex_data(raw_data)
        self.vertex_data = vertex_data
        self.color_data = color_data

        self.verts = OpenGlVerts(vertex_data, color_data)
        self.vert_options = args_to_dict(self.verts.draw)

    def get_options(self):
        pass

    def add_options(self, options, name):
        option_lyt = QtGui.QVBoxLayout()
        option_lyt.addStretch()

        label = QtGui.QLabel()
        label.setText(name + '\n----------')
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
