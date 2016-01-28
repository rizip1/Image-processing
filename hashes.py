import cv2
import numpy as np


def p_hash(img):
    '''
    Creates pHash string from given image.
    '''
    big_kernel = 64
    small_kernel = int(big_kernel / 4)

    img = _get_shrinked_grayscale(img, big_kernel, big_kernel)
    img = np.float32(img) / 255.0 
    img = cv2.dct(img)
   
    average = _get_top_left_average(img, small_kernel)
    hash_string = []
    
    for i in range(small_kernel):
         for j in range(small_kernel):
            if (img[i][j] < average):
                hash_string.append('1')
            else:
                hash_string.append('0')

    return ''.join(hash_string)


def a_hash(img):
    '''
    Creates aHash string from given image.
    '''
    img = _get_shrinked_grayscale(img, 16, 16)
    average = _get_intensity_average(img)
    hash_string = []

    for row in img:
        for value in row:
            if (value < average):
                hash_string.append('1')
            else:
                hash_string.append('0')

    return ''.join(hash_string)


def d_hash(img):
    '''
    Creates dHash string from given image.
    '''
    img = _get_shrinked_grayscale(img, 17, 16)
    hash_string = []

    for i in range(len(img)):
        for j in range(len(img[i]) - 1):
            if img[i, j] < img[i, j + 1]:
                hash_string.append('1')
            else:
                hash_string.append('0')

    return ''.join(hash_string)


def compare_hashes(hash1, hash2):
    '''
    Compare two string hashes and retrieve float
    in range [0,1] representing their similarity.
    The lower number represents higher similarity.
    '''
    if (len(hash1) != len(hash2)):
        return None
    
    mismatches = 0
    for i in range(len(hash1)):
        if (hash1[i] != hash2[i]):
            mismatches += 1
    
    return float(mismatches) / len(hash1)


def _get_shrinked_grayscale(img, width, height):
    '''
    Shrink image using given width and height and
    convert it into grayscale.
    '''
    img = cv2.resize(img, (width, height), fx=0, fy=0,
                     interpolation = cv2.INTER_AREA)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def _get_intensity_average(img):
    height = len(img)
    width = len(img[0])
    average_sum = 0

    for row in img:
        for value in row:
            average_sum += value

    return average_sum / (height * width)


def _get_top_left_average(img, size):
    '''
    Return average from top left pixels excluding first(DC).
    Top left area is determined by `size` param.
    '''
    average = 0
    for i in range(size):
        for j in range(size):
            average += img[i][j]
    
    average -= img[0][0]
    average /= ((size**2) - 1)
    return average

