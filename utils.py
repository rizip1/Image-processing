import os
import sys
import cv2
import shutil
import subprocess
import re

def _check_params(argv):
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


def _get_length(filename):
    result = subprocess.Popen(['ffprobe', filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    content = [x for x in result.stdout.readlines()]
    for item in content:
        item = str(item)
        m = re.search('Duration: (.+), start', item)
        if m:
            matched =  m.group(1).split(":")
            return (int(matched[1]) * 60) + float(matched[2])


def frame_parser(source, to, every_nth, ext):
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


def create_hash_structure(directory, number_of_dirs = 10):
    os.chdir(directory)

    for advertising in os.listdir(os.getcwd()):
        os.mkdir(os.path.join(advertising, advertising))
        os.chdir(advertising)
        for i in range(number_of_dirs):
            os.mkdir(os.path.join(advertising, str(i + 1)))
            os.mknod(os.path.join(advertising, str(i + 1), 'target_frame.txt'))
        os.chdir("../")


def get_video_props(dest):
    '''
    Used to get information about videos length
    and size in desired folder which must in
    same form as folder for video tester.
    '''
    total_length = 0
    total_size = 0
    for set_id in os.listdir(dest):
        if not os.path.isdir(os.path.join(dest, set_id)):
            continue
        for video in os.listdir(os.path.join(dest, set_id)):
            if not os.path.isdir(os.path.join(dest, set_id, video)):
                continue
            for rec in os.listdir(os.path.join(dest, set_id, video)):
                if not os.path.isdir(os.path.join(dest, set_id, video, rec)):
                    continue
                total_length += (_get_length(os.path.join(dest, set_id, video,
                                                         rec, rec + '.mp4')))
                size = (os.path.getsize(os.path.join(dest, set_id, video,
                                                     rec, rec + '.mp4')))
                size = size / (1024 * 1024)
                total_size += size
    results = {}
    results['total_length'] = (total_length / 100)
    results['total_size'] = (total_size / 100)
    results['to_twenty'] = results['total_size'] / results['total_length'] * 20
    return results


if __name__ == '__main__':
    action = sys.argv[1]
    if (action == 'create_dirs'):
        if (len(sys.argv) > 3):
            create_hash_structure(sys.argv[2], int(sys.argv[3]))
        else:
            create_hash_structure(sys.argv[2])
    elif (action == 'parse_images'):
        argv = sys.argv
        _check_params(argv)
        ext = (argv[4], 'jpg')[len(argv) > 3]
        frame_parser(source = argv[2], to = argv[3], every_nth = argv[4],
                      ext = ext)
    elif (action == 'get_props'):
        results = get_video_props(sys.argv[2])
        print('Total length:', results['total_length'])
        print('Total_size:', results['total_size'])
        print('To 20:', results['to_twenty'])

