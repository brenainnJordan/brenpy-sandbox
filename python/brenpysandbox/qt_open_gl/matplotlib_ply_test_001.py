'''
Created on Apr 22, 2017

@author: User
'''

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



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
    
    f.close()
    #outF.close()

    np_verts = np.array(vert_array, dtype=np.float32)

    print 'Finished reading PLY...'
    return vert_array


def plot_points(points, colours):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
     
    # s = size of points, can either be scalar or an array of size x*y
    plt.scatter(points[::3], points[1:][::3], zs=points[2:][::3], s=2)#, c=colours)
    plt.show()

path = r'C:\Partition\Bren\Projects\3D\Photogrametry\RichmondPark\RichmondParl_Tree3\Tree_003_001.1.ply'
points = readPly(path)
plot_points(points, None)
