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


def find_screen(source, dest):
    #shutil.rmtree(self.out_dir + "/" + self.THRESH_DIR)
    os.chdir(source)
    i = 0
    for advertising in os.listdir(os.getcwd()):
        os.chdir(advertising)
        os.chdir(advertising)
        i += 1
        j = 0
        for sample in os.listdir(os.getcwd()):
            os.chdir(sample)
            j += 1
            
            # it also turns into grayscale
            img = cv2.imread('img.jpg', 0)
            original_image = _get_original_image()
            hash_original = _get_original_hash(original_image)
            _get_best_results(img, i, j, dest)

            os.chdir("../")
        os.chdir("../")
        os.chdir("../")


def _get_best_results(img, i, j, dest):
    threshold_values = [50, 70, 90, 110, 130, 150, 170, 190]

    for value in threshold_values:
        ret, thresh = cv2.threshold(img, value, 255, cv2.THRESH_BINARY)

        #ret, thresh = cv2.threshold(img,0,255,
        #cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        _find_contours(img, i, j)


def _find_contours(img, i ,j, dest):
    '''
    Find contours in the thresholded image, keep only the largest
    ones, and initialize our screen contour
    '''
    (cnts, _) = cv2.findContours(img.copy(), cv2.RETR_TREE, 
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:3]

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
                    cv2.imwrite(os.path.join(dest, str(i) + str(j)))


def _get_original_image():
    try:
        with open('target_frame.txt', "r") as target:
            temp = target.read().splitlines()
            frame = temp[0]
            frame += ".jpg"
    except IOError:
        raise("Error while reading target_frame text file!")
    img = cv2.imread(os.path.join(os.getcwd(), "../../frames", frame))
    return img


def _get_original_hash(image):
    return p_hash(image)


def _is_big_enough(img, w, h):
    h_orig, w_orig, channels = img.shape
    return ((w * h) >= ((h_orig * w_orig) / 20))


def _has_best_score(img):
    hash_string = p_hash(img)
    difference = compare_hashes(hash_string, hash_original)
    if (difference < best_value):
        best_value = difference
        return True
    else:
        return False
    

if __name__ == "__main__":
    source = sys.argv[1]
    dest = os.path.join(os.getcwd(), 'src/screen_detector')
    find_screen(source, dest)

