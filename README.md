# Image-processing

*Experimental tools for detecting snapshot position in advertising.*

### Using screen detector
Check you have openCV, matplotlib and numpy installed.
To evaluate data in the given folder using chosen perceptual hash
algorithm and method use:
``` python
python utils.py create_dirs <method> <perc_hash> <hist_title>
```
**hist_title**: specifies histogram title

**method**
* 1 for OTSU
* 2 for ITERATE
* 3 for ADAPTIVE_MEAN
* 4 for ADAPTIVE_GAUSSIAN
* 5 for CANNY

**perc_hash**
* p for pHash
* a for aHash
* d for dHash

After the script finishes the results will be store in cwd/src directory.

### Create data structure
The script requires data structure as shown in the image.

To create the initial structure create an empty directory for each advertising in your destination folder and then run:
``` python
python screen_detector.py <data_folder> <count>
```
**count** is the number of folders to be created in each advertising directory.

### Parse video to frames
You can use:
``` python
python utils.py parse_images <source> <to> <everyNth> <ext>
```

**source** is the video to parse

**to** is where to put the frames

**everyNth** specifies which every n-th frame to capture. To capture all pass 1

**ext** is extension. Default is jpg.
