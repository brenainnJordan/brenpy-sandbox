'''
Created on 11 Mar 2018

@author: Bren
'''

import numpy as np
from scipy import spatial
from operator import itemgetter

def tracking_test():
    # get candidates
    x,y = np.mgrid[1:6, 2:8]
    grid = zip(x.ravel(), y.ravel())
    candidates = spatial.KDTree(grid)
    print grid
    # get points
    points = np.array([[0, 0], [0.1, 0.1], [2.1, 2.9]])
    print points
    
    tracked_points = [None]*len(points)
    
    
    # sort candidates by distances to each point
    distances_list, candidate_ids = candidates.query(points, k=None)
    #candidate_ids = np.array([np.array(i) for i in candidate_ids])
    print type(distances_list)
    print type(candidate_ids[0])
    print candidate_ids
    #print [np.delete(i, [2] for i in candidate_ids]), np.array([2, 12, 18]))
    
    print [candidates.data[i[0]] for i in candidate_ids]
    
    # sort distances by closest first keeping reference to point id
    point_distances = [(point_id, distances) for point_id, distances in enumerate(distances_list)]
    sorted_point_distances = sorted(point_distances, key=itemgetter(1))
    
    # sort point ids by shortest distance to candidates
    sorted_point_ids = [i[0] for i in sorted_point_distances] 
    
    # get tracked points 
    for tracking_point_id in sorted_point_ids:
        # get nearest candidate 
        tracked_point_id = candidate_ids[tracking_point_id][0]
        tracked_point = candidates.data[tracked_point_id]
        print len(candidate_ids[tracking_point_id])
        tracked_points[tracking_point_id] = tracked_point
        print tracking_point_id, tracked_point_id, tracked_point
        
        # remove tracked point from next candidates
        for point_id in sorted_point_ids[tracking_point_id:]:
            if tracked_point_id in candidate_ids[point_id]:
                candidate_ids[point_id].remove(tracked_point_id)
            #candidate_ids[point_id] = np.delete(candidate_ids[point_id], [tracked_point_id]) 
    
    print tracked_points
    
tracking_test()

test = range(10)
print test
print test[1:]
