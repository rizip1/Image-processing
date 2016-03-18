import cv2
import sys
import os
import shutil

def check_params(argv):
    if len(argv) < 4:
        sys.stderr.write('Please provide all required arguments.')
        sys.exit()

def _prepare_folder(to):
    path = os.path.join(os.getcwd(), to)
    if (os.path.isdir(path)):
        for item in os.listdir(path):
            item = os.path.join(path, item)
            if (os.path.isdir(item)):
                shutil.rmtree(os.path.join(path, item))
            else:
                os.remove(item)
    else:
      os.mkdir(path)
    return path

def obtain_images(source, to, every_nth, ext):
    every_nth = int(every_nth)
    total_count = 0
    saved_count = 0

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        cap.open()
    path = _prepare_folder(to)

    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret == False:
            break

        if ((total_count % every_nth) == 0):
            saved_count += 1

        if (saved_count < 9):
            name = '0{0}.{1}'.format(saved_count, ext)
        else:
            name = '{0}.{1}'.format(saved_count, ext)

        cv2.imwrite(os.path.join(path, name), frame)
        total_count += 1

    cap.release()
    cv2.destroyAllWindows()
    print('Number of frames scanned: {}'.format(total_count))
    print('Number of frames saved: {}'.format(saved_count))

if __name__ == '__main__':
    argv = sys.argv
    check_params(argv)
    ext = (argv[3], 'jpg')[len(argv) > 3]
    obtain_images(source = argv[1], to = argv[2], every_nth = argv[3],
                  ext = ext)
