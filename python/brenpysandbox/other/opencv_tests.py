'''
Created on Nov 27, 2017

@author: User

https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_tutorials.html

'''

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
