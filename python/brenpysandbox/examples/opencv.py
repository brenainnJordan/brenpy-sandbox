'''
Created on Nov 27, 2017

@author: Brenainn Jordan

open cv sandbox and testing

useful links:
https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html

'''

import sys
import os
import numpy
import cv2


def threshold_blue_mult():
    '''
    Threshold the blue channel and multiply image
    '''
    
    # get image
    img_path = r'C:\Partition\Bren\Pictures\dorritoMan.jpg'
    img = cv2.imread(img_path)
    
    # normalise pixel values
    img = img/255.0
    img_shape = img.shape
    
    # threshold and invert blue channel
    blue_channel = img[:,:,0]
    ret, mask = cv2.threshold(blue_channel, 0.05, 1.0, cv2.THRESH_BINARY)
    #mask_inv = cv2.bitwise_not(mask)
    mask_inv = 1.0 - mask
    
    # reshape threshold mask from single channel to 3 channels
    s = mask_inv.size
    mask_flat = mask_inv.reshape([s])
    mask_repeat = mask_flat.repeat(3)
    mask_repeat_reshape = mask_repeat.reshape(img_shape)
    
    # multiply by image
    img_masked = img*mask_repeat_reshape
    
    # debug
    print img[0]
    print img_masked[0]
    
    # view result
    cv2.imshow('image', img_masked)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def corner_detection():
    # get image
    img_path = r'C:\Partition\Bren\Pictures\dorritoMan.jpg'
    img = cv2.imread(img_path)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = numpy.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)
    
    #result is dilated for marking the corners, not important
    dst = cv2.dilate(dst, None)
    
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst>0.01*dst.max()] = [0, 0, 255]
    
    cv2.imshow('dst', img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()


def adjust_gamma(image, gamma=1.0):
    '''
    https://www.pyimagesearch.com/2015/10/05/opencv-gamma-correction/
    '''
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = numpy.array([((i / 255.0) ** invGamma) * 255
        for i in numpy.arange(0, 256)]).astype("uint8")
 
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def blob_detection():
    '''
    https://www.learnopencv.com/blob-detection-using-opencv-python-c/
    '''
    
    # get image
    img_path = r'C:\Partition\Bren\Pictures\dorritoMan.jpg'
    #img_path = r'C:\Partition\Bren\Projects\dev\python\standalone_tools\examples\BlobTest.jpg'
    #img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(img_path)
    img = img/255.0
    
    # get bgr channels (not rgb!)
    b_channel = img[:,:,0]
    g_channel = img[:,:,1]
    r_channel = img[:,:,2]
    
    # threshold using blue channel
    ret, mask = cv2.threshold(b_channel, 0.2, 1.0, cv2.THRESH_BINARY)
    #mask_inv = cv2.bitwise_not(mask)
    mask_inv = 1.0 - mask
    
    # multiply red and green channels
    img = r_channel*g_channel*mask_inv
    
    # normalise
    img = img-img.min()
    img = img*(1.0/img.max())
    
    # adjust gamma
    img_8bit = numpy.uint8(img*255)
    img_8bit = adjust_gamma(img_8bit, gamma=1.0)
    
    # blur test
    #img = cv2.blur(img,(10,20))
    
    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()
     
    # Change thresholds
    params.minThreshold = 10;
    params.maxThreshold = 200;
     
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 10
     
    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1
     
    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.87
     
    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01
     
    # Create a detector with the parameters
    ver = (cv2.__version__).split('.')
    print ver
    if int(ver[0]) < 3 :
        detector = cv2.SimpleBlobDetector(params)
    else : 
        detector = cv2.SimpleBlobDetector_create(params)
    
    # Detect blobs.
    #img_8bit = numpy.uint8(img*255)
    keypoints = detector.detect(img_8bit)
    print keypoints
     
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(
        img_8bit, keypoints, numpy.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
     
    # Show keypoints
    cv2.imshow("Keypoints", im_with_keypoints)
    cv2.waitKey(0)


def video_capture():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow("Capture", frame)
        cv2.waitKey(5)
    cv2.destroyAllWindows()

def bg_subtraction_1():
    """
        Requires 64bit python (or something, anaconda runs fine)
    """
    
    src_dir = r"E:\photogrammetry\turkishTempleModel"
    #blur_outdir = r"E:\photogrammetry\turkishTempleModel\1_bg_blurred"
    #black_outdir = r"E:\photogrammetry\turkishTempleModel\1_bg_black"
    
    if not os.path.exists(src_dir):
        print "directory does not exist: ", src_dir
        return
    
    for sub_dir in ["03"]:
        in_dir = os.path.join(src_dir, sub_dir)
        out_dir = os.path.join(src_dir, "bg_blurred", sub_dir)
        
        for d in [in_dir, out_dir]:
            if not os.path.exists(d):
                print "directory does not exist: ", d
                return
        
        filenames = os.listdir(in_dir)
        filenames = [i for i in filenames if i.endswith(".jpg") or i.endswith(".JPG")]
        
        #cap = cv2.VideoCapture(os.path.join(dir, "image_%03d.jpg"))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        fgbg = cv2.createBackgroundSubtractorMOG2()
        
        for i, filename in enumerate(filenames):
            img_path = os.path.join(in_dir, filename)
            img = cv2.imread(img_path)
            #ret, frame = cap.read()
            
            fgmask = fgbg.apply(img)
            #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
            ret, mask = cv2.threshold(fgmask, 20, 255, cv2.THRESH_BINARY)
            blurred_mask = cv2.blur(mask,(50, 50))
            ret, mask = cv2.threshold(blurred_mask, 25, 255, cv2.THRESH_BINARY)
            blurred_mask = cv2.blur(mask,(50, 50))
    
            #blurred_mask = adjust_gamma(blurred_mask, gamma=2)
            blurred_mask = blurred_mask/255.0
            #blurred_mask = numpy.clip(blurred_mask, 0, 255)
            
            s = blurred_mask.size
            mask_flat = blurred_mask.reshape([s])
            mask_repeat = mask_flat.repeat(3)
            mask_repeat_reshape = mask_repeat.reshape(img.shape)
            
            
            # black bg output
            masked_img = img*mask_repeat_reshape
            
            """
            black_outpath = os.path.join(black_outdir, filename)
            
            res = cv2.imwrite(black_outpath, masked_img)
            
            if res:
                print "written: ", black_outpath
            """
            
            # fill in the gaps with blurred original image
            inv_blurred_mask = 1.0-blurred_mask
            
            mask_flat = inv_blurred_mask.reshape([s])
            mask_repeat = mask_flat.repeat(3)
            inv_blurred_mask_reshape = mask_repeat.reshape(img.shape)
            
            blurred_img = cv2.blur(img, (200, 200))
            masked_blurred_img = blurred_img*inv_blurred_mask_reshape
            
            bg_blur_img = masked_img+masked_blurred_img
            
            blur_outpath = os.path.join(out_dir, filename)
            
            res = cv2.imwrite(blur_outpath, bg_blur_img)
            
            if res:
                print "written: ", blur_outpath
        
        """
        cv2.imshow('frame',fgmask)
        #cv2.imshow('frame', frame)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        """
        
    
    #cap.release()
    #cv2.destroyAllWindows()

def rename_images():
    dir = r"E:\photogrammetry\turkishTempleModel\1"
    files = os.listdir(dir)
    for i, file in enumerate(files):
        name = "image_{:03d}.jpg".format(i)
        os.rename(os.path.join(dir, file), os.path.join(dir, name))

def blur_red_bg():
    src_dir = r"E:\photogrammetry\turkishTempleModel"
    
    if not os.path.exists(src_dir):
        print "directory does not exist: ", src_dir
        return
    
    for sub_dir in ["01", "02", "03"]:
        in_dir = os.path.join(src_dir, sub_dir)
        out_dir = os.path.join(src_dir, "red_blurred", sub_dir)
        
        for d in [in_dir, out_dir]:
            if not os.path.exists(d):
                print "directory does not exist: ", d
                return
        
        filenames = os.listdir(in_dir)
        filenames = [i for i in filenames if i.endswith(".jpg") or i.endswith(".JPG")]
        
        #cap = cv2.VideoCapture(os.path.join(dir, "image_%03d.jpg"))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        fgbg = cv2.createBackgroundSubtractorMOG2()
        
        for i, filename in enumerate(filenames):
            img_path = os.path.join(in_dir, filename)
            img = cv2.imread(img_path)/255.0
            
            blue_channel = img[:,:,0]
            green_channel = img[:,:,1]
            red_channel = img[:,:,2]
            
            #blue_channel = blue_channel/255.0
            #green_channel = green_channel/255.0
            #red_channel = red_channel/255.0
            
            red_mult = red_channel
            red_mult -= green_channel
            red_mult -= blue_channel
            red_mult -= red_mult.min()
            red_mult *= 1.0/red_mult.max()
            
            thresh = 0.8
            red_mult[red_mult < thresh] = 0.0
            red_mult[red_mult > thresh] = 1.0
            #print red_mult
            #red_mult *= 255.0
            #ret, red_mult = cv2.threshold(red_mult, 0.2, 1.0, cv2.THRESH_BINARY)
            
            red_mult = red_mult.reshape([red_mult.size])
            red_mult = red_mult.repeat(3)
            red_mult = red_mult.reshape(img.shape)
            
            #test_img = img*red_mult
            test_img = red_mult*255
            
            outpath = os.path.join(out_dir, filename)
            
            res = cv2.imwrite(outpath, test_img)
            
            if res:
                print "written: ", outpath
            

#threshold_blue_mult()
#corner_detection()
#blob_detection()
#video_capture()
#bg_subtraction_1()
#rename_images()
blur_red_bg()
