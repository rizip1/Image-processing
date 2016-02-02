import subprocess
import sys
import os
import re

'''
Used to get information about videos length
and size in desired folder which must in
same form as folder for video tester.
'''

def get_length(filename):
    result = subprocess.Popen(['ffprobe', filename],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    content = [x for x in result.stdout.readlines()]
    for item in content:
        item = str(item)
        m = re.search('Duration: (.+), start', item)
        if m:
            matched =  m.group(1).split(":")
            return (int(matched[1]) * 60) + float(matched[2])


def get_results(dest):
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
                total_length += (get_length(os.path.join(dest, set_id, video,
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


if __name__ == "__main__":
    results = get_results(sys.argv[1])
    print('Total length:', results['total_length'])
    print('Total_size:', results['total_size'])
    print('To 20:', results['to_twenty'])

