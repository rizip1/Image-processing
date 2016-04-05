import cv2
import sys
import collections
import os
import shutil
import matplotlib.pyplot as plt
import numpy as np

from hashes import compare_hashes

class ScreenDetector:
    OTSU = 1
    ITERATE = 2
    ADAPTIVE_MEAN = 3
    ADAPTIVE_GAUSSIAN = 4
    CANNY = 5
    SEARCHED_FRAMES = 50

    
    def __init__(self, source, dest, title='Threshold and hash results'):
        self.source = source
        self.dest = dest
        self.dest_images = os.path.join(dest, 'screen_detector/')
        self.title = title
        self.best_score = 1
        self.hash_original = ''
        self.original_image = None
        self.best_image = None
        self.stats = {}

    
    def find_screen(self, method):
        '''
        Iterate through all the advertising in the given folder, find screen
        for each image and create results.txt and histogram.png files
        in given_folder/results/ directory.
        '''
        self._clean_or_create_dest_dir()
        average_error = 0
        os.chdir(self.source)

        for advertising in os.listdir(os.getcwd()):
            os.chdir(advertising)
            os.chdir(advertising)
            for sample in os.listdir(os.getcwd()):
                self.best_score = 1
                os.chdir(sample)
                image_name = '{0}_{1}.jpg'.format(advertising,
                                                 (sample, '0{0}'.format(sample))
                                                 [int(sample) < 10])
                print(image_name)

                # also turns into grayscale
                img = cv2.imread('img.jpg', 0)
                image_data = self._get_original_image_data()
                self.hash_original = self._get_original_hash(image_data['img'])
                self._call_recognition_method(img, method)

                cv2.imwrite(os.path.join(self.dest_images, image_name), 
                                         self.best_image)
                accuracy = self._get_position_accuracy(image_data['position'])
                average_error += accuracy
                self.stats[image_name] = accuracy

                os.chdir('../')
            os.chdir('../')
            os.chdir('../')
        y_max = self._put_stats_into_file()
        self._create_hist(y_max)
        return float(average_error) / len(self.stats) 
    
    
    def _iterate_thresholds(self, img):
        '''
        Detect tv in the image using iteration through threshold values.
        '''
        threshold_values = [50, 70, 90, 110, 130, 150, 170, 190, 210]

        for value in threshold_values:
            ret, thresh = cv2.threshold(img, value, 255, cv2.THRESH_BINARY)
            self._find_contours(img, thresh)

    
    def _otsu(self, img):
        '''
        Detect tv in the image using Otsu's binarization.
        '''
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        ret, thresh = cv2.threshold(blur, 0, 255,
                                    cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        self._find_contours(img, thresh)


    def _adaptive_threshold_mean(self, img):
        '''
        Detect tv in the image using adaptive threshold.
        '''
        blur = cv2.medianBlur(img, 5)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        self._find_contours(img, thresh)
    
    
    def _adaptive_threshold_gaussian(self, img):
        '''
        Detect tv in the image using adaptive threshold.
        '''
        blur = cv2.medianBlur(img, 5)
        thresh = cv2.adaptiveThreshold(blur, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        self._find_contours(img, thresh)

    
    def _canny_edge(self, img):
        '''
        Detect tv in the image using canny edge detection.
        '''
        sigma = 0.33
        med = np.median(img)

        l_bound = int(max(0, (1.0 - sigma) * med))
        u_bound = int(min(255, (1.0 + sigma) * med))

        canny = cv2.Canny(img, l_bound, u_bound)
        self._find_contours(img, canny)
    
    
    def _find_contours(self, img, filtered):
        '''
        Find contours in the thresholded image, keep only the largest
        ones and from these choose one with best hash score.
        '''
        _, cnts, _ = cv2.findContours(filtered.copy(), cv2.RETR_TREE, 
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
                if (self._is_big_enough(img, w, h)):
                    roi = img[y:y+h, x:x+w]
                    if (self._has_best_score(roi)):
                        self.best_image = roi
        
    
    def _get_original_image_data(self):
        '''
        Return image object and position in which it appears
        in the original video.
        '''
        try:
            with open('target_frame.txt', 'r') as target:
                temp = target.read().splitlines()
                frame = temp[0]
        except IOError:
            raise Exception('Error while reading target_frame text file!')
        img = cv2.imread(os.path.join(os.getcwd(), '../../frames',
                         frame + ".jpg"))
        return {'img': img, 'position': frame}

    
    def _get_original_hash(self, img):
        return per_hash(img, convert=True)

    
    def _is_big_enough(self, img, w, h):
        h_orig, w_orig = img.shape
        return ((w * h) >= ((h_orig * w_orig) / 20))

    
    def _has_best_score(self, img):
        hash_string = per_hash(img, convert=False)
        difference = compare_hashes(hash_string, self.hash_original)
        if (difference < self.best_score):
            self.best_score = difference
            return True
        else:
            return False

    
    def _call_recognition_method(self, img, method):
        if (method == ScreenDetector.OTSU):
            self._otsu(img)
        elif (method == ScreenDetector.ITERATE):
            self._iterate_thresholds(img)
        elif (method == ScreenDetector.ADAPTIVE_MEAN):
            self._adaptive_threshold_mean(img)
        elif (method == ScreenDetector.ADAPTIVE_GAUSSIAN):
            self._adaptive_threshold_gaussian(img)
        elif (method == ScreenDetector.CANNY):
            self._canny_edge(img)
        else:
            raise Exception('Unsupported method provided.')
        if (self.best_image is None):
            self.best_image = img
        
    
    def _get_position_accuracy(self, right_position):
        right_position = int(right_position)
        start = right_position - ScreenDetector.SEARCHED_FRAMES
        if (start <= 0):
            start = 1
        end = right_position + ScreenDetector.SEARCHED_FRAMES
        
        best_fit = 1
        best_fit_position = 0
        
        hash2 = per_hash(self.best_image, convert=False)
        for i in range(start, end):
            pos = str(i)
            if (i < 10):
                pos = '0' + pos
            img = cv2.imread('../../frames/{0}.jpg'.format(pos))
            hash1 = per_hash(img, convert=True)
            diff = compare_hashes(hash1, hash2)
            if (diff < best_fit):
                best_fit = diff
                best_fit_position = i
        return abs(right_position - best_fit_position)

    
    def _clean_or_create_dest_dir(self):
        try:
            if (os.path.isdir(self.dest_images)):
                for item in os.listdir(self.dest):
                    if (os.path.isdir(os.path.join(self.dest, item))):
                        shutil.rmtree(os.path.join(self.dest, item))
                    else:
                        os.remove(os.path.join(self.dest, item))
            else:
                if (not os.path.isdir(self.dest)):
                    os.mkdir(self.dest)
            os.mkdir(self.dest_images)
        except:
            raise Exception('Could not prepare destination directory.')

    
    def _put_stats_into_file(self):
        '''
        Put statistics into results.txt file and return
        y axis threshold for _create_hist function.
        '''
        try:
            os.mkdir(os.path.join(self.dest, 'results'))
            file_name = 'results/results.txt'
            with open(os.path.join(self.dest, file_name), 'w+')  as results:
                self.stats = collections.OrderedDict(sorted(self.stats.items()))
                
                for key in self.stats.keys():
                    results.write('{0}: {1}\n'.format(key,
                        str(self.stats[key])))
                
                results.write('\n')
                final_stats = {}
                for item in self.stats.values():
                    if (item in final_stats):
                        final_stats[item] += 1
                    else:
                        final_stats[item] = 1
                for key in final_stats:
                    results.write('{0}: {1}\n'.format(key, final_stats[key]))
                return max(final_stats.values())
        except:
            raise Exception('Could not save the results.')

    
    def _create_hist(self, y_max):
        plt.hist(list(self.stats.values()),
                bins=ScreenDetector.SEARCHED_FRAMES+1,
                range=(0, ScreenDetector.SEARCHED_FRAMES+1), width=1, 
                color='pink')
        plt.xlabel('Error')
        plt.ylabel('Frames count')
        plt.title(self.title)

        plt.axis([0, ScreenDetector.SEARCHED_FRAMES+1, 0, y_max+1])
        plt.grid(True)

        hist_path = os.path.join(self.dest, 'results/histogram.png')
        plt.savefig(hist_path)


if __name__ == '__main__':
    source = sys.argv[1]
    dest = os.path.join(os.getcwd(), 'src/')
    
    if (len(sys.argv) > 4):
        sd = ScreenDetector(source, dest, title=sys.argv[4])
    else:
        sd = ScreenDetector(source, dest)
    
    h_name = 'p_hash'
    if (len(sys.argv) > 2):
        if (len(sys.argv) > 3):
            h_argv = sys.argv[3]
            if (h_argv == 'a'):
                h_name = 'a_hash'
            elif (h_argv == 'd'):
                h_name = 'd_hash'
        per_hash = getattr(__import__('hashes', fromlist=[h_name]), h_name)
        average_error = sd.find_screen(int(sys.argv[2]))
    else:
        per_hash = getattr(__import__('hashes', fromlist=[h_name]), h_name)
        average_error = sd.find_screen(ScreenDetector.ITERATE)
    print('Average error: ', average_error)

