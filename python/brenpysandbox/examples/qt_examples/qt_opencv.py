'''
Created on Dec 3, 2017

@author: Brenainn Jordan

useful links:
https://github.com/marcel-goldschen-ohm/PyQtImageViewer/blob/master/QtImageViewer.py

to get aruco libs:
pip install opencv-contrib-python

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
FACE_SEQUENCE = r'E:\jobs\reel\material\RSC\image_sequences\jpg\1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER\1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER_%d.jpg'
#FACE_SEQUENCE = r'E:\jobs\reel\material\RSC\image_sequences\png\10_1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER\0_1700_128_NPS_VDU_AC_Bren_Jordan_showreel_Tempest_footage_Clip_10_ProRes_MASTER_%03d.png'
CRAPPY_BLOB_TEST = r'C:\Users\Bren\Videos\MVI_2747.MOV'

class ImgTracker(QtGui.QWidget):
    '''
    Image tracking class
    
    Nice threaded version:
    http://kurokesu.com/main/2016/08/01/opencv-usb-camera-widget-in-pyqt/
    
    '''
    
    def __init__(self, parent=None):
        super(ImgTracker, self).__init__()
        
        # user options
        self._track_faces = False
        self._track_blobs = False
        self._tracked_blobs = False
        self._track_acuro = False
        self._max_radius = 100.0
        self._invert = False
        
        self._show_clean = True
        
        # blob options
        self._min_threshold = 10
        self._max_threshold = 200
        self._min_area = 20
        self._min_circularity = 0.8
        self._min_convexity = 0.2
        
        # initialise video capture
        self._track = True
        self.img = None
        self.mQImage = None
        
        # acuro dictionary
        self.acuro_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        
        # blob detector and params
        self.get_blob_detector()
        self.track = False
        self.trail_len = 10
        self.frame = 0
        
        # face params
        cascPath = os.path.join(CASCADE_DIR, 'haarcascade_frontalface_default.xml')
        self.faceCascade = cv2.CascadeClassifier(cascPath)
        
        # instance Qt loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1)
    
    
    def get_blob_detector(self):
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
        
        if int(ver[0]) < 3 :
            self.blob_detector = cv2.SimpleBlobDetector(params)
        else : 
            self.blob_detector = cv2.SimpleBlobDetector_create(params)
    

    def get_blobs(self, draw=False):
        
        keypoints = self.blob_detector.detect(self.track_img)
        
        if draw:
            self.anoted_img = cv2.drawKeypoints(
                self.anoted_img,
                keypoints,
                numpy.array([]),
                (0,0,255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        points = numpy.array([kp.pt for kp in keypoints])
        
        return points
        
    
    def get_acuro_markers(self):
        
        # Acuro detection needs a grayscale image
        gray = cv2.cvtColor(self.track_img, cv2.COLOR_BGR2GRAY)
    
        res = cv2.aruco.detectMarkers(gray, self.acuro_dictionary)
        #   print(res[0],res[1],len(res[2]))
    
        if len(res[0]) > 0:
            cv2.aruco.drawDetectedMarkers(self.anoted_img, res[0],res[1])
        
        #return img, res
    
    def edit_img(self, img):
        if self._invert:
            img = 255 - img
        
        return img
    
    def get_img(self, edit=True, detect=True):
        if self.img is None:
            return
        
        self.track_img = numpy.copy(self.img)
        
        if edit:
            self.track_img = self.edit_img(self.track_img)
        
        if self._show_clean:
            self.anoted_img = numpy.copy(self.img)
        else:
            self.anoted_img = numpy.copy(self.track_img)
        
        if detect:
            if self._track_faces:
                
                gray = cv2.cvtColor(self.track_img, cv2.COLOR_BGR2GRAY)
                
                faces = self.faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
            
                # Draw a rectangle around the faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(self.anoted_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if self._track_acuro:
                self.get_acuro_markers()
            
            if self._track_blobs:
                self.get_blobs()
                
                if self.track:
                    self.track_blobs()
            
            if self._tracked_blobs:
                self.draw_tracked_blobs()
        
        height, width, byteValue = self.img.shape
        byteValue = byteValue * width

        cv2.cvtColor(self.anoted_img, cv2.COLOR_BGR2RGB, self.anoted_img)
        
        self.mQImage = QtGui.QImage(
            self.anoted_img, width, height, byteValue, QtGui.QImage.Format_RGB888)
    
    
    def init_blobs(self):
        '''
        Get all blobs in current frame and store as initial positions
        '''
        #points = self.get_blobs()
        #self.point_tracks = [deque([tuple(i.astype(int))], maxlen=self.trail_len) for i in points]
        blobs = self.blob_detector.detect(self.track_img)
        self.tracked_blobs = [blobs]  
        self.track = True
    
    
    def track_blobs_old(self):
        '''
        For each stored point find the nearest and append to tracks
        '''
        thickness = 2
        
        #points = self.get_blobs()
        points = self.blob_detector.detect(self.track_img)
        tree = spatial.KDTree(points)
        
        previous_points = [i[-1] for i in self.point_motion]
        
        distances, ids = tree.query(self.previous_points)
        
        """    
        unique_ids = []
        
        for id in ids:
            if id in unique_ids:
                unique_ids.append(id)
            else:
                unique_ids.append(None)
        """
        
        nearest = points[ids]
        self.previous_points = nearest
        
        for n, pts in zip(nearest, iter(self.point_tracks)):
            pts.appendleft(tuple(n.astype(int)))
            
            # draw lines
            for i in xrange(1, len(pts)):
                if pts[i - 1] is None or pts[i] is None:
                    continue
                cv2.line(self.anoted_img, pts[i - 1], pts[i], (0, 0, 255), thickness)
    
    def track_blobs(self, image_sequence, edit=True):
        # init blobs
        image = image_sequence[0]
        if edit:
            image = self.edit_img(image)
        
        blobs = self.blob_detector.detect(image)
        
        if len(blobs) == 0:
            print 'no blobs to track'
            return
        
        self.tracked_blobs = [blobs]
        
        # track sequence
        for i, image in enumerate(image_sequence[1:]):
            if edit:
                image = self.edit_img(image)
            
            candidate_blobs = self.blob_detector.detect(image)
            
            if len(candidate_blobs) > 0:
                tracked_blobs = self.track_unique_blobs(self.tracked_blobs[-1], candidate_blobs)
            else:
                print 'no blob candidates at frame: ', i
                tracked_blobs = self.tracked_blobs[-1]
            
            self.tracked_blobs.append(tracked_blobs)
        
        self.blob_sequences = self.tracked_blobs_to_blob_sequences(self.tracked_blobs)
        
        self._tracked_blobs = True
    
    def tracked_blobs_to_blob_sequences(self, tracked_blobs):
        """ could be quicker using numpy reshape
        """
        blob_sequences = numpy.transpose(tracked_blobs)
        return blob_sequences
    
        blob_sequences = [[i] for i in tracked_blobs[0]]
        
        for frame in tracked_blobs:
            for i, blob in enumerate(frame):
                blob_sequences[i].append(blob)
        
        return blob_sequences
        
    
    def get_sorted_indices(self, items):
        """ sort items and return corresponding indices of original list
        """
        
        id_items = [(i, item) for i, item in enumerate(items)]
        sorted_id_items = sorted(id_items, key=itemgetter(1))
        sorted_ids = [i[0] for i in sorted_id_items]
        
        return sorted_ids 
    
    def track_unique_blobs(self, blobs, candidate_blobs):
        '''
        For each stored point find the nearest unique neighbour and append to tracks
        '''
        
        # get keypoints
        points = [kp.pt if kp is not None else [0, 0] for kp in blobs]
        candidates = [kp.pt for kp in candidate_blobs]
        
        # create kdtree
        candidates = spatial.KDTree(candidates)
        
        # get points
        #tracked_points = [None]*len(points)
        
        # create empy blob list
        tracked_blobs = [None]*len(points) 
        
        # sort candidates by distances to each point
        distances_list, candidate_ids = candidates.query(points, k=None, distance_upper_bound=self._max_radius)
        
        # sort distances by closest first keeping reference to point id
        #point_distances = [(point_id, distances) for point_id, distances in enumerate(distances_list)]
        #sorted_point_distances = sorted(point_distances, key=itemgetter(1))
        
        # sort point ids by shortest distance to candidates
        #sorted_point_ids = [i[0] for i in sorted_point_distances]
        #sorted_point_ids = self.get_sorted_indices(distances_list)
        sorted_point_ids = distances_list.argsort()
        
        # get tracked points 
        for i in range(len(blobs)):
            tracking_point_id = sorted_point_ids[i]
            
            if len(candidate_ids[tracking_point_id]) == 0:
                continue
            
            # get nearest candidate
            tracked_point_id = candidate_ids[tracking_point_id][0]
            tracked_blob = candidate_blobs[tracked_point_id]
            
            tracked_blobs[tracking_point_id] = tracked_blob
            
            # remove tracked point from next candidates
            #occurences = []
            for point_id in sorted_point_ids[i+1:]:
                if not len(candidate_ids[point_id]):
                    continue
                
                if candidate_ids[point_id][0] == tracked_point_id:
                    candidate_ids[point_id].pop(0)
                    distances_list[point_id].pop(0)
                    # supposedly faster
                    # l = deque(['a', 'b', 'c', 'd'])
                    # l.popleft()
                """
                #if tracked_point_id in candidate_ids[point_id]:
                try:
                    #index = candidate_ids[point_id].index(tracked_point_id)
                    index = numpy.where(candidate_ids[point_id] == tracked_point_id)[0][0]
                    occurences.append(index)
                #except ValueError:
                except IndexError:
                    continue
                print index
                candidate_ids[point_id] = numpy.delete(candidate_ids[point_id], index)
                distances_list[point_id] = numpy.delete(distances_list[point_id], index)
                """
            # updated sorted ids
            sorted_point_ids = distances_list.argsort()
        
        # todo
        # validate we haven't used the same point twice
        
        return tracked_blobs
    
    

    def draw_tracked_blobs(self, thickness=2):
        # draw lines
        for blob_sequence in self.blob_sequences:
            for i in xrange(self.frame-self.trail_len, self.frame+1):
                if i < 1:
                    continue
                
                if blob_sequence[i - 1] is None or blob_sequence[i] is None:
                    continue
                
                #print blob_sequence[i - 1].pt
                p1 = tuple(int(i) for i in blob_sequence[i - 1].pt)
                p2 = tuple(int(i) for i in blob_sequence[i].pt)
                #p2 = tuple(blob_sequence[i].astype(int))
                
                cv2.line(self.anoted_img, p1, p2, (0, 0, 255), thickness)
        
        # draw blobs
        self.anoted_img = cv2.drawKeypoints(
            self.anoted_img,
            self.tracked_blobs[self.frame],
            numpy.array([]),
            (0,0,255),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
    
    def paint_image(self):
        if self._track or self._tracked_blobs:
            self.get_img()
        
        if self.img is None:
            return
        
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.drawImage(0, 0, self.mQImage)
        self.painter.end()
        
    def paintEvent(self, QPaintEvent):
        self.paint_image()


class ImageWidget(ImgTracker):
    '''
    basic qt image viewer
    '''
    
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent=parent)
        
        #img_path = CAT_BLOBS
        #img_path = SOFT_BLOBS
        img_path = FACES
        
        self.img = cv2.imread(img_path)
    
    def paintEvent(self, QPaintEvent):
        self.paint_image()
        # once we have our initial detection we no longer need to track
        self._track = False


class WebcamWidget(ImgTracker):
    '''
    basic qt webcam viewer
    
    Nice threaded version:
    http://kurokesu.com/main/2016/08/01/opencv-usb-camera-widget-in-pyqt/
    
    '''
    
    def __init__(self, parent=None):
        super(WebcamWidget, self).__init__(parent=parent)
        
        # initialise video capture
        self.cap = cv2.VideoCapture(0)
        #self._adjust_capture_settings() # <-- this breaks my webcam!
   
    
    def _adjust_capture_settings(self):
        '''
        ** Caution **
        This seems to break my webcam!
        
        property indices:        
        4 CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream.
        5 CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream.
        11 CV_CAP_PROP_BRIGHTNESS Brightness of the image (only for cameras).
        12 CV_CAP_PROP_CONTRAST Contrast of the image (only for cameras).
        13 CV_CAP_PROP_SATURATION Saturation of the image (only for cameras).
        14 CV_CAP_PROP_HUE Hue of the image (only for cameras).
        15 CV_CAP_PROP_GAIN Gain of the image (only for cameras).
        16 CV_CAP_PROP_EXPOSURE Exposure (only for cameras).
        '''
        
        self.cap.set(4, 300)
        self.cap.set(5, 200)
        self.cap.set(11, 0.1)
    
    
    def paintEvent(self, QPaintEvent):
        ret, self.img = self.cap.read()
        self.paint_image()


class ImageSequenceWidget(ImgTracker):
    """ Read and track image sequence
    """
    def __init__(self, parent=None):
        super(ImageSequenceWidget, self).__init__(parent=parent)
        
        #sequence_path = SEQUENCE
        #sequence_path = VIDEO
        #sequence_path = FACE_SEQUENCE
        sequence_path = CRAPPY_BLOB_TEST
        
        self.cap = cv2.VideoCapture(sequence_path)
        
        # load whole sequence into memory
        ret, img = self.cap.read()
        self.img_sequence = []
        
        while ret:
            #img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # remove alpha channel
            self.img_sequence.append(img)
            ret, img = self.cap.read()
        
        self.img = self.img_sequence[0]
        
        #ret, self.img = self.cap.retrieve()
        #ret, self.img = self.cap.frame()
    
    
    def set_frame(self, frame):
        self.frame = frame
        self.img = self.img_sequence[frame]
    
    def paintEvent(self, QPaintEvent):
        self.paint_image()


class ImageGUI(QtGui.QMainWindow):
    '''
    Basic image viewer with buttons and layout
    '''
    
    def __init__(self, parent=None):
        super(ImageGUI, self).__init__(parent)
        
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_lyt = QtGui.QHBoxLayout()
        self.central_widget.setLayout(main_lyt)
        
        img_lyt = QtGui.QVBoxLayout()
        main_lyt.addLayout(img_lyt)
        
        #self.img_widget = ImageWidget()
        #self.img_widget = WebcamWidget()
        self.img_widget = ImageSequenceWidget()
        self.sequence = True
        
        img_lyt.addWidget(self.img_widget)
        
        btn_lyt = QtGui.QVBoxLayout()
        btn_lyt.addStretch()
        main_lyt.addLayout(btn_lyt, 0)
        
        # playback options
        self.start_frame = 0
        self.current_frame = 0
        
        if self.sequence:
            self.end_frame = len(self.img_widget.img_sequence)
        else:
            self.end_frame = 10
        
        # image options
        self.clean_check = QtGui.QCheckBox('show clean image')
        self.clean_check.setChecked(True)
        self.clean_check.clicked.connect(self.toggle_clean)
        btn_lyt.addWidget(self.clean_check)
        
        self.invert_check = QtGui.QCheckBox('invert')
        self.invert_check.clicked.connect(self.toggle_invert)
        btn_lyt.addWidget(self.invert_check)
        
        # track options
        label = QtGui.QLabel('track options:')
        btn_lyt.addWidget(label)
        
        self.face_check = QtGui.QCheckBox('faces')
        self.face_check.clicked.connect(self.toggle_face)
        btn_lyt.addWidget(self.face_check)
        
        self.acuro_check = QtGui.QCheckBox('acuro')
        self.acuro_check.clicked.connect(self.toggle_acuro)
        btn_lyt.addWidget(self.acuro_check)
        
        # blob tracking options
        self.blobs_check = QtGui.QCheckBox('blobs')
        self.blobs_check.clicked.connect(self.toggle_blobs)
        btn_lyt.addWidget(self.blobs_check)
        
        self.blob_min_thresh_spin = self.add_spin(
            'min threshold',
            self.img_widget._min_threshold,
            self.edit_blob_min_thresh,
            btn_lyt
        )
        
        self.blob_max_thresh_spin = self.add_double_spin(
            'max threshold',
            self.img_widget._max_threshold,
            self.edit_blob_max_thresh,
            btn_lyt
        )
        
        self.blob_min_area_spin = self.add_double_spin(
            'min area',
            self.img_widget._min_area,
            self.edit_blob_min_area,
            btn_lyt
        )
        
        self.blob_min_circularity_spin = self.add_double_spin(
            'min circularity',
            self.img_widget._min_circularity,
            self.edit_blob_min_circularity,
            btn_lyt
        )
        
        self.blob_min_convexity_spin = self.add_double_spin(
            'min convexity',
            self.img_widget._min_convexity,
            self.edit_blob_min_convexity,
            btn_lyt
        )
        
        init_btn = QtGui.QPushButton('init blobs')
        init_btn.clicked.connect(self.img_widget.init_blobs)
        btn_lyt.addWidget(init_btn)
        
        track_btn = QtGui.QPushButton('track blobs')
        track_btn.clicked.connect(self.track_blobs)
        btn_lyt.addWidget(track_btn)
        
        # other stuff
        label = QtGui.QLabel('other stuff:')
        btn_lyt.addWidget(label)
        
        btn = QtGui.QPushButton('debug')
        btn.clicked.connect(self._get_shape)
        btn_lyt.addWidget(btn)
        
        main_lyt.setStretch(0, 1)
        
        # playback controls
        play_lyt = QtGui.QHBoxLayout()
        
        self.start_frame_spin = self.add_spin(
            None, # 'startFrame',
            self.start_frame,
            self.edit_start_frame,
            play_lyt,
            max_value=self.end_frame
        )
        
        play_lyt.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Expanding))
        
        self.play_btn = QtGui.QPushButton('play')
        self.stop_btn = QtGui.QPushButton('stop')
        
        play_lyt.addWidget(self.play_btn)
        play_lyt.addWidget(self.stop_btn)
        
        self.current_frame_spin = self.add_spin(
            None, # 'frame',
            self.current_frame,
            self.edit_current_frame,
            play_lyt,
            min_value=self.start_frame,
            max_value=self.end_frame
        )
        
        play_lyt.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Expanding))
        
        self.end_frame_spin = self.add_spin(
            None, # 'endFrame',
            self.end_frame,
            self.edit_end_frame,
            play_lyt,
            min_value=self.start_frame
        )
        
        #play_lyt.setStretch(0, 0, 1, 0, 0, 0, 1, 0, 0)
        
        img_lyt.addLayout(play_lyt)
        
        # time slider
        self.time_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.time_slider.setMinimum(self.start_frame)
        self.time_slider.setMaximum(self.end_frame)
        self.time_slider.valueChanged.connect(self.slide_to_frame)
        
        img_lyt.addWidget(self.time_slider)
    
    
    @staticmethod
    def add_double_spin(label, value, method, lyt, min_value=0.0, max_value=1000.0):
        spin_lyt = QtGui.QHBoxLayout()
        
        if label is not None:
            label = QtGui.QLabel(label)
            spin_lyt.addWidget(label)
        
        spin= QtGui.QDoubleSpinBox()
        spin.setMinimum(min_value)
        spin.setMaximum(max_value)
        spin.setValue(value)
        spin.valueChanged.connect(method)
        
        spin_lyt.addWidget(spin)
        
        lyt.addLayout(spin_lyt)
        
        return spin
    
    @staticmethod
    def add_spin(label, value, method, lyt, min_value=0, max_value=1000):
        spin_lyt = QtGui.QHBoxLayout()
        
        if label is not None:
            label = QtGui.QLabel(label)
            spin_lyt.addWidget(label)
        
        spin= QtGui.QSpinBox()
        spin.setMinimum(min_value)
        spin.setMaximum(max_value)
        spin.setValue(value)
        spin.valueChanged.connect(method)
        
        spin_lyt.addWidget(spin)
        
        lyt.addLayout(spin_lyt)
        
        return spin
    
    # tracking update methods
    def update_tracker(self):
        if self.img_widget._track is False:
            self.img_widget.get_img()
    
    def update_blob_tracker(self):
        self.img_widget.get_blob_detector()
        self.update_tracker()
    
    # image methods
    def toggle_clean(self):
        self.img_widget._show_clean = self.clean_check.isChecked()
        self.update_tracker()
    
    def toggle_invert(self):
        self.img_widget._invert = self.invert_check.isChecked()
        self.update_tracker()
    
    # track methods
    def toggle_face(self):
        self.img_widget._track_faces = self.face_check.isChecked()
        self.update_tracker()
    
    def toggle_blobs(self):
        self.img_widget._track_blobs = self.blobs_check.isChecked()
        self.update_tracker()
    
    def toggle_acuro(self):
        self.img_widget._track_acuro = self.acuro_check.isChecked()
        self.update_tracker()
    
    def track_blobs(self):
        self.img_widget.track_blobs(self.img_widget.img_sequence, edit=True)
    
    # playback options
    def edit_start_frame(self):
        self.start_frame = self.start_frame_spin.value()
        self.time_slider.setMinimum(self.start_frame)
        self.end_frame_spin.setMinimum(self.start_frame)
        self.current_frame_spin.setMinimum(self.start_frame)
    
    def edit_end_frame(self):
        self.end_frame = self.end_frame_spin.value()
        self.time_slider.setMaximum(self.end_frame)
        self.start_frame_spin.setMaximum(self.end_frame)
        self.current_frame_spin.setMaximum(self.end_frame)
    
    def edit_current_frame(self):
        self.current_frame = self.current_frame_spin.value()
        self.time_slider.setValue(self.current_frame)
        
        if self.sequence:
            self.img_widget.set_frame(self.current_frame)
    
    def slide_to_frame(self):
        self.current_frame = self.time_slider.value()
        self.current_frame_spin.setValue(self.current_frame)
        
        if self.sequence:
            self.img_widget.set_frame(self.current_frame)
    
    # blob tracking methods
    def edit_blob_min_thresh(self):
        self.img_widget._min_threshold = self.blob_min_thresh_spin.value()
        self.update_blob_tracker()
        
    def edit_blob_max_thresh(self):
        self.img_widget._max_threshold = self.blob_max_thresh_spin.value()
        self.update_blob_tracker()
    
    def edit_blob_min_area(self):
        self.img_widget._min_area = self.blob_min_area_spin.value()
        self.update_blob_tracker()
    
    def edit_blob_min_circularity(self):
        self.img_widget._min_circularity = self.blob_min_circularity_spin.value()
        self.update_blob_tracker()
    
    def edit_blob_min_convexity(self):
        self.img_widget._min_convexity = self.blob_min_convexity_spin.value()
        self.update_blob_tracker()
    
    
    def _get_shape(self):
        # testing
        #ret, img = self.img_widget.cap.read()
        height, width, byteValue = self.img_widget.img.shape
        print height, width, byteValue

    

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    w = ImageGUI()
    w.resize(1280, 720)
    w.show()
    app.exec_()
