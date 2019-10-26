'''
Created on Apr 22, 2017

@author: User
'''

import OpenGL.GL as GL
import OpenGL.GL.shaders
import ctypes
import pygame
import numpy

vertex_shader = """
#version 330
in vec4 position;
void main()
{
   gl_Position = position;
}
"""

fragment_shader = """
#version 330
void main()
{
   gl_FragColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
}
"""


path = r'C:\Partition\Bren\Projects\3D\Photogrametry\RichmondPark\RichmondParl_Tree3\Tree_003_001.1.ply'

def readPly(path):
    
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
            vert_array += vert
    
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
    
    print 'Finished reading PLY...'
    return np_verts


def create_object(shader):
    # Create a new VAO (Vertex Array Object) and bind it
    vertex_array_object = GL.glGenVertexArrays(1)
    GL.glBindVertexArray( vertex_array_object )
    
    # Generate buffers to hold our vertices
    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)
    
    # Get the position of the 'position' in parameter of our shader and bind it.
    position = GL.glGetAttribLocation(shader, 'position')
    GL.glEnableVertexAttribArray(position)
    
    # Describe the position data layout in the buffer
    GL.glVertexAttribPointer(position, 4, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))
    
    # Send the data over to the buffer
    GL.glBufferData(GL.GL_ARRAY_BUFFER, 48, vertices, GL.GL_STATIC_DRAW)
    
    # Unbind the VAO first (Important)
    GL.glBindVertexArray( 0 )
    
    # Unbind other stuff
    GL.glDisableVertexAttribArray(position)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    
    return vertex_array_object


    GL.glBindVertexArray( vertex_array_object )
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
    GL.glBindVertexArray( 0 )