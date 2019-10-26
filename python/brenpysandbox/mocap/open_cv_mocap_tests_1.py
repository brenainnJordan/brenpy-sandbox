'''
Created on 18 Oct 2018

@author: Bren
'''


import sys
import os
import numpy
import cv2

from scipy import spatial
from collections import deque
from operator import itemgetter

from PySide import QtGui, QtCore
from scipy.constants.constants import point
from numpy import inf

OPEN_CV_DIR = r'E:\software\opencv\opencv'
CASCADE_DIR = os.path.join(OPEN_CV_DIR, r'sources\data\haarcascades')

IMAGE_DIR = r'E:\dev\python\standalone_tools\examples\images'
DORRITO = r'C:\Partition\Bren\Pictures\dorritoMan.jpg'
BLOBS = os.path.join(IMAGE_DIR, 'BlobTest.jpg')
CAT_BLOBS = os.path.join(IMAGE_DIR, 'cat_blobs.jpg')
SOFT_BLOBS = os.path.join(IMAGE_DIR, 'soft_blobs.png')

SEQUENCE_TEST = r'E:\jobs\reel\material\particleFill\ArielRubble_008_0001.png'
SEQUENCE = r'E:\jobs\reel\material\particleFill\ArielRubble_008_%04d.png'
VIDEO = r'E:\jobs\reel\material\RSC_tempest_Intel_720.mp4'
FACES = r'C:\Users\Bren\Pictures\Vic-Reeves-and-Bob-Mortimer.jpg'
#FACE_SEQUENCE = r'E:\jobs\reel\material\RSC\image_sequences\png\10_1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER\0_1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER_%03d.png'
CRAPPY_BLOB_TEST = r'C:\Users\Bren\Videos\MVI_2747.MOV'

# good for marker testing and face tracking
TEST_SEQUENCE = r'E:\jobs\reel\material\RSC\image_sequences\jpg\1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER\1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER_%d.jpg'


def kd_tree_test():
    """Test multiple "frames" of points"""

    test = numpy.array([
        [0, 0, 1],
        [0, 0, 2],
        [1, 0, 0],
        [2, 1, 0],
    ])

    tree = spatial.KDTree(test)

    print tree.query(
        [
            [0, 0, 2],
            [0, 0, 1.6]
        ]
    )


kd_tree_test()

# # TO SLOW!!
# class UnTrackedMarkerCandidate(object):
#     """blah"""
#
#     def __init__(self, id, position):
#         self.id = id
#         self.position = position
#
#
# class UnTrackedMarker(object):
#     """blah"""
#
#     def __init__(self):
#         # each untracked marker has a candidate for the next frame
#         self._candidate = None
#
#     def set_candidate(self, id, position=None):
#         self._candidate = UnTrackedMarkerCandidate(id, position)
#
#
# class UnTrackedMarkerList(object):
#     """Untracked markers for one frame of image sequence"""
#
#     def __init__(self, markers):
#         self._markers = [UnTrackedMarker(i) for i in markers]
#
#     def find_candidates(self):
#         pass


class UntrackedBlobs(object):
    def __init__(self, keypoints):
        self._keypoints = keypoints
        self._points = numpy.array([kp.pt for kp in self._keypoints])
        self._tree = spatial.KDTree(self._points)

    def track_next_frame(self, candidate_blobs, max_distance=0.1):
        blob_distances, blob_ids = candidate_blobs.tree().query(
            self.points(),
            distance_upper_bound=max_distance
        )

    def tree(self):
        return self._tree

    def keypoints(self):
        return self._keypoints

    def points(self):
        return self._points

    def anotate_image(self, img):
        """Draw blobs on img"""

        return cv2.drawKeypoints(
            img,
            self._keypoints,
            numpy.array([]),
            (0, 0, 255),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )


class Tracker(object):
    """Blah"""

    def __init__(self):
        # blob options
        self._min_threshold = 10
        self._max_threshold = 200
        self._min_area = 20
        self._min_circularity = 0.8
        self._min_convexity = 0.2

        # current frame data
        self._blobs = []

    def define_blob_detector(self):
        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = self._min_threshold
        params.maxThreshold = self._max_threshold

        # Filter by Area.
        params.filterByArea = True
        params.minArea = self._min_area

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = self._min_circularity

        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = self._min_convexity

        # Filter by Inertia
        params.filterByInertia = False
        params.minInertiaRatio = 0.2

        # Create a detector with the parameters
        ver = (cv2.__version__).split('.')

        if int(ver[0]) < 3:
            self.blob_detector = cv2.SimpleBlobDetector(params)
        else:
            self.blob_detector = cv2.SimpleBlobDetector_create(params)

    def detect_blobs(self, draw=False):
        """Get blobs for current frame"""

        self._blob_keypoints = self.blob_detector.detect(self.track_img)

        print type(self._blob_keypoints[0])
        print dir(self._blob_keypoints[0])

        if False:
            self.anoted_img = cv2.drawKeypoints(
                self.anoted_img,
                self._blob_keypoints,
                numpy.array([]),
                (0, 0, 255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

#         self._blob_points = numpy.array([kp.pt for kp in keypoints])
