import subprocess
import sys
import os
import re

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

if __name__ == "__main__":
    print(get_length(sys.argv[1]))
    size = int(os.path.getsize(sys.argv[1]))
    size = size / (1024 * 1024)
    print(size)

