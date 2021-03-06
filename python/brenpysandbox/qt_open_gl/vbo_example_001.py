'''
:from
Introduction to Shaders: First steps (Basic Geometry)
http://pyopengl.sourceforge.net/context/tutorials/shader_1.html

:dependencies
testingcontext:
pyvrml97
pydispatch
pydispatcher
Pillow
'''

import sys

from OpenGLContext import testingcontext
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import BaseContext
from OpenGL.GL import shaders
from OpenGL.GLU import *
#import OpenGL_accelerate


'''
OpenGLContext testingcontext allows for the use of Pygame, wxPython, or GLUT GUI systems with the same code.
These imports retrieve an appropriate context for this machine.
If you have not installed any "extra" packages, such as Pygame or wxPython,
this will likely be a GLUT context on your machine.
'''

class TestContext( BaseContext ):

    """Creates a simple vertex shader..."""
    # The OnInit method is called *after* there is a valid OpenGL rendering Context.
    # You must be very careful not to call (most) OpenGL entry points
    # until the OpenGL context has been created
    # (failure to observe this will often cause segfaults or other extreme behaviour).
    def OnInit( self ):
        VERTEX_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }""", GL_VERTEX_SHADER)
        
        '''After a vertex is processed by the vertex shader, it passes through a number of fixed-function processes, including the "clipping" process, which may turn a single vertex into multiple vertices in order to only render geometry "ahead" of the near clipping plane.
        Thus if a triangle is "poking into your eye" the GL will generate two vertices that are at the points where the triangle intersects the near clipping plane and create 3 triangles from the original one triangle (the same is true of all of the clipping plans for the frustum).
        Fragment Shader
        The fixed-function operations will generate "fragments", which can be loosely thought of as a "possible pixel". They may represent a sub-sampling interpolation value, or a value that will eventually be hidden behind another pixel (overdrawn). Our renderer will be given a (large number of) fragments each of which will have a position calculated based on the area of the triangle vertices (gl_Position values) that our vertex shader generated.
        The fragment shader only *needs* to do one thing, which is to generate a gl_FragColor value, that is, to determine what colour the fragment should be. The shader can also decide to write different colours to different colour buffers, or even change the position of the fragment, but its primary job is simply to determine the colour of the pixel (a vec4() value).
        In our code here, we create a new colour for each pixel, which is a pure green opaque (the last 1) value. We assign the value to the (global, built-in) gl_FragColor value and we are finished.
        '''
        
        FRAGMENT_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }""", GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
        
        '''Vertex Buffer Data Objects (VBOs)
        Modern OpenGL wants you to load your data onto your video card as much as possible. For geometric data, this is generally done via a Vertex Buffer Object. These are flexible data-storage areas reserved on the card, with various strategies available for streaming data in/out.
        For our purposes we can think of the VBO as a place on the card to which we are going to copy our vertex-description data. We'll use a Numpy array to define this data, as it's a convenient format for dealing with large arrays of numeric values.
        Modern cards work best with a format where all of the data associated with a single vertex is "tightly packed" into a VBO, so each record in the array here represents all of the data needed to render a single vertex. Since our shader only needs the vertex coordinate to do its rendering, we'll use 3 floating-point values. (Note: not doubles, as in a Python float, but 3 machine floating point values).
        Modern OpenGL only supports triangle and point-type geometry, so the simplest form of drawing (though not necessarily the fastest) is to specify each vertex of a set of triangles in order. Here we create one triangle and what looks like a square to the viewer (two triangles with two shared vertices).
        The vbo.VBO class simply takes an array-compatible format and stores the value to be pushed to the card later. It also takes various flags to control the more advanced features, but we'll look at those later.
        '''

        self.vbo = vbo.VBO(
            array( [
                [  0, 1, 0 ],
                [ -1,-1, 0 ],
                [  1,-1, 0 ],
                [  2,-1, 0 ],
                [  4,-1, 0 ],
                [  4, 1, 0 ],
                [  2,-1, 0 ],
                [  4, 1, 0 ],
                [  2, 1, 0 ],
            ],'f')
        )
    
    #We've now completed our application initialization, we have our shaders compiled and our VBO ready-to-render. Now we need to actually tell OpenGLContext how to render our scene. The Render() method of the context is called after all of the boilerplate OpenGL setup has been completed and the scene should be rendered in model-space. OpenGLContext has created a default Model-View matrix for a perspective scene where the camera is sitting 10 units from the origin. It has cleared the screen to white and is ready to accept rendering commands.
    
    def Render( self, mode):
        """Render the geometry for the scene."""
        '''Rendering
        We tell OpenGL to use our compiled shader, this is a simple GLuint that is an opaque token that describes the shader for OpenGL. Until we Use the shader, the GL is using the fixed-function (legacy) rendering pipeline.
                shaders.glUseProgram(self.shader)
        Now we tell OpenGL that we want to enable our VBO as the source for geometric data. There are two VBO types that can be active at any given time, a geometric data buffer and an index buffer, the default here is the geometric buffer.
        '''
        try:
            self.vbo.bind()
            try:
                '''Here we tell OpenGL to process vertex (location) data from our vertex pointer (here we pass the VBO). The VBO acts just like regular array data, save that it is stored on the card, rather than in main memory. The VBO object is actually passing in a void pointer (None) for the array pointer, as the start of the enabled VBO is taken as the 0 address for the arrays.
                Note the use here of the "typed" glVertexPointerf function, while this is a convenient form for this particular tutorial, most VBO-based rendering will use the standard form which includes specifying offsets, data-types, strides, and the like for interpreting the array. We will see the more involved form in the next tutorial.
                '''
                glEnableClientState(GL_VERTEX_ARRAY);
                glVertexPointerf( self.vbo )
                # Finally we actually tell OpenGL to draw some geometry. Here we tell OpenGL to draw triangles using vertices, starting with the offset 0 and continuing for 9 vertices (that is, three triangles). glDrawArrays always draws "in sequence" from the vertex array. We'll look at using indexed drawing functions later.
                glDrawArrays(GL_TRIANGLES, 0, 9)
                # Having completed rendering our geometry, we clean up the OpenGL environment. We unbind our vbo, so that any traditional non-VBO-using code can operate, and unbind our shader so that geometry that uses the fixed-function (legacy) rendering behaviour will work properly.
            finally:
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY);
        finally:
            shaders.glUseProgram( 0 )

#We need to actually run the code when operating as a top-level script. The TestingContext import above also gave us an appropriate mainloop function to call.

if __name__ == "__main__":
    TestContext.ContextMainLoop()


'''When run from the command-line, we should see a triangle and a rectangle in solid green
 floating over a black background, as seen in our screenshot above.
Terms:
frustum
the viewing "stage" of your world, i.e. the part of the world which is visible to the "camera",
includes a near and far clipping plane, as well as clipping planes for the left, right,
top and bottom
GLSL
the OpenGL Shading Language, there are two levels of shading language defined within OpenGL,
the earlier of the two is a low-level assembly-like language.
The later, GLSL is a slightly higher-level C-like language,
this is the language we will be using in these tutorials.
There are also third-party languages, such as Cg,
which can compile the same source-code down to e.g. DirectX and/or OpenGL renderers.
legacy
OpenGL is an old standard, the traditional API has been largely deprecated
by the OpenGL standards board, the vendors generally support the old APIs,
but their use is officially discouraged.
The Legacy APIs had a single rendering model which was customized
via a large number of global state values.
The new APIs are considerably more flexible, but require somewhat more effort to use.
OpenGLContext Docs Tutorials Previous Next

This code-walkthrough tutorial is generated from the shader_1.py script
in the OpenGLContext source distribution.
'''