import cv2
import sys
import collections
import os
import shutil
import matplotlib.pyplot as plt

from hashes import p_hash, compare_hashes


class ScreenDetector:
    OTSU = 1
    ITERATE = 2
    SEARCHED_FRAMES = 50


    def __init__(self, source, dest):
        self.source = source
        self.dest = dest
        self.best_score = 1
        self.hash_original = ""
        self.original_image = None
        self.best_image = None
        self.stats = {}


    def find_screen(self, method):
        self._clean_or_create_dest_dir()
        average_error = 0
        os.chdir(source)

        for advertising in os.listdir(os.getcwd()):
            os.chdir(advertising)
            os.chdir(advertising)
            for sample in os.listdir(os.getcwd()):
                self.best_score = 1
                os.chdir(sample)
                image_name = advertising + '_' + sample + '.jpg'
                print(image_name)

                # also turns into grayscale
                img = cv2.imread('img.jpg', 0)
                image_data = self._get_original_image_data()
                self.hash_original = self._get_original_hash(image_data['img'])
                self._call_recognition_method(img, method)
                
                cv2.imwrite(os.path.join(self.dest, image_name), 
                                         self.best_image)
                accuracy = self._get_position_accuracy(image_data['position'])
                average_error += accuracy
                self.stats[image_name] = accuracy

                os.chdir("../")
            os.chdir("../")
            os.chdir("../")
        self._put_stats_into_file()
        self._create_hist()
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
         blur = cv2.GaussianBlur(img, (5, 5), 0)
         ret, thresh = cv2.threshold(blur, 0, 255,
                                     cv2.THRESH_BINARY+cv2.THRESH_OTSU)
         self._find_contours(img, thresh)


    def _find_contours(self, img, thresh):
        '''
        Find contours in the thresholded image, keep only the largest
        ones, and initialize our screen contour
        '''
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
                if (self._is_big_enough(img, w, h)):
                    roi = img[y:y+h, x:x+w]
                    if (self._has_best_score(roi)):
                        self.best_image = roi
        

    def _get_original_image_data(self):
        try:
            with open('target_frame.txt', "r") as target:
                temp = target.read().splitlines()
                frame = temp[0]
        except IOError:
            raise("Error while reading target_frame text file!")
        img = cv2.imread(os.path.join(os.getcwd(), "../../frames",
                         frame + ".jpg"))
        return {'img': img, 'position': frame}


    def _get_original_hash(self, img):
        return p_hash(img, convert=True)


    def _is_big_enough(self, img, w, h):
        h_orig, w_orig = img.shape
        return ((w * h) >= ((h_orig * w_orig) / 20))


    def _has_best_score(self, img):
        hash_string = p_hash(img, convert=False)
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
        else:
            raise("Unsupported method provided.")
        

    def _get_position_accuracy(self, right_position):
        right_position = int(right_position)
        start = right_position - ScreenDetector.SEARCHED_FRAMES
        if (start <= 0):
            start = 1
        end = right_position + ScreenDetector.SEARCHED_FRAMES
        
        best_fit = 1
        best_fit_position = 0

        hash2 = p_hash(self.best_image, convert=False)
        for i in range(start, end):
            pos = str(i)
            if (i < 10):
                pos = "0" + pos
            img = cv2.imread('../../frames/' + pos + ".jpg")
            hash1 = p_hash(img, convert=True)
            diff = compare_hashes(hash1, hash2)
            if (diff < best_fit):
                best_fit = diff
                best_fit_position = i
        return abs(right_position - best_fit_position)


    def _clean_or_create_dest_dir(self):
        try:
            if (os.path.isdir(self.dest)):
                for item in os.listdir(self.dest):
                    if (os.path.isdir(os.path.join(self.dest, item))):
                        shutil.rmtree(os.path.join(self.dest, item))
                    else:
                        os.remove(os.path.join(self.dest, item))
            else:
                os.mkdir(self.dest)
        except:
            raise("Could not prepare destination directory.")


    def _put_stats_into_file(self):
        try:
            os.mkdir(os.path.join(self.dest, 'results'))
            file_name = 'results/results.txt'
            with open(os.path.join(self.dest, file_name), 'w+')  as results:
                self.stats = collections.OrderedDict(sorted(self.stats.items()))
                
                for key in self.stats.keys():
                    results.write(key + ":" + str(self.stats[key]) + "\n")
        except:
            raise("Could not save the results.")


    def _create_hist(self):
        plt.hist(list(self.stats.values()),
                bins=ScreenDetector.SEARCHED_FRAMES+1,
                range=(0, ScreenDetector.SEARCHED_FRAMES+1), width=1, 
                color='pink')
        plt.xlabel('Error')
        plt.ylabel('Advertising count')
        plt.title('Threshold and hash results')

        plt.axis([0, ScreenDetector.SEARCHED_FRAMES+1, 0, len(self.stats)+1])
        plt.grid(True)

        hist_path = os.path.join(self.dest, 'results/histogram.png')
        plt.savefig(hist_path)


if __name__ == "__main__":
    source = sys.argv[1]
    dest = os.path.join(os.getcwd(), 'src/screen_detector')
    sd = ScreenDetector(source, dest)
    average_error = sd.find_screen(ScreenDetector.ITERATE)
    print("Average error: ", average_error)

