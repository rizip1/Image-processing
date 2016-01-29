#!/usr/bin/python

import numpy as np
import cv2
import sys
import glob
import os
import shutil

from hashes import p_hash, compare_hashes


best_value = 1
hash_original = ""
original_image = ""
best_image = None
stats = []


def find_screen(source, dest):
    #shutil.rmtree(self.out_dir + "/" + self.THRESH_DIR)
    global hash_original
    global best_value
    global stats
    global best_image

    os.chdir(source)
    i = 0
    for advertising in os.listdir(os.getcwd()):
        os.chdir(advertising)
        os.chdir(advertising)
        i += 1
        j = 0
        for sample in os.listdir(os.getcwd()):
            best_value = 1
            os.chdir(sample)
            j += 1
            
            # it also turns into grayscale
            img = cv2.imread('img.jpg', 0)
            original_image_data = _get_original_image_data()
            hash_original = _get_original_hash(original_image_data['img'])
            #otsu(img, i, j, dest)
            _get_best_results(img, i, j, dest)
            
            accuracy = _get_position_accuracy(original_image_data['position'])
            print(accuracy)
            stats.append(accuracy)

            os.chdir("../")
        os.chdir("../")
        os.chdir("../")
    print("STATS", stats)

def _get_best_results(img, i, j, dest):
    threshold_values = [50, 70, 90, 110, 130, 150, 170, 190]

    for value in threshold_values:
        ret, thresh = cv2.threshold(img, value, 255, cv2.THRESH_BINARY)

        #ret, thresh = cv2.threshold(img,0,255,
        #cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        _find_contours(img, thresh, i, j, dest)


def otsu(img, i, j, dest):
     blur = cv2.GaussianBlur(img,(5,5),0)
     ret3,th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
     _find_contours(img, th, i, j, dest)



def _find_contours(img, thresh, i ,j, dest):
    '''
    Find contours in the thresholded image, keep only the largest
    ones, and initialize our screen contour
    '''
    global best_image

    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, 
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:4]

    # loop over our contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) >= 4:
            # take screen from origin picture 
            # which belongs to contour
            x, y, w, h = cv2.boundingRect(approx)
            if (_is_big_enough(img, w, h)):
                roi = img[y:y+h, x:x+w]
                if (_has_best_score(roi)):
                    best_image = roi
                    cv2.imwrite(os.path.join(dest, str(i) + str(j) + ".jpg"), 
                                roi)
    

def _get_original_image_data():
    try:
        with open('target_frame.txt', "r") as target:
            temp = target.read().splitlines()
            frame = temp[0]
    except IOError:
        raise("Error while reading target_frame text file!")
    img = cv2.imread(os.path.join(os.getcwd(), "../../frames", frame + ".jpg"))
    return {'img': img, 'position': frame}

def _get_original_hash(image):
    return p_hash(image, convert=True)


def _is_big_enough(img, w, h):
    h_orig, w_orig = img.shape
    return ((w * h) >= ((h_orig * w_orig) / 20))


def _has_best_score(img):
    global best_value
    global hash_original

    hash_string = p_hash(img, convert=False)
    difference = compare_hashes(hash_string, hash_original)
    if (difference < best_value):
        best_value = difference
        return True
    else:
        return False
    

def _get_position_accuracy(right_position):
    global best_image
    
    start = int(right_position) - 50
    if (start <= 0):
        start = 1
    end = int(right_position) + 50
    
    best = 1
    best_position = 0

    hash2 = p_hash(best_image, convert=False)
    for i in range(start, end):
        pos = str(i)
        if (i < 10):
            pos = "0" + pos
        img = cv2.imread('../../frames/' + pos + ".jpg")
        hash1 = p_hash(img, convert=True)
        diff = compare_hashes(hash1, hash2)
        if (diff < best):
            best = diff
            best_position = i
    print("HASH", best)
    return abs(int(right_position) - best_position)


if __name__ == "__main__":
    source = sys.argv[1]
    dest = os.path.join(os.getcwd(), 'src/screen_detector')
    find_screen(source, dest)

