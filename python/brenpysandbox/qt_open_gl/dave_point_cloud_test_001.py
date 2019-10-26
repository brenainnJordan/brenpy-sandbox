import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def thing(): 
    points = np.random.rand(1000, 3).astype(np.float32) * 100.0
    colours = np.random.rand(1000, 4).astype(np.float32)
    colours[:, 3] = 1.0
    
    print type(points)
    print points
    print points[:, 0]
    return None
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # s = size of points, can either be scalar or an array of size x*y
    plt.scatter(points[:, 0], points[:, 1], zs=points[:, 2], s=5, c=colours)
    plt.show()

test = [1,2,3,4,5,6]
print test[:: 3]