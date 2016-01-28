import cv2

def d_hash(img):
    '''
    Creates dHash string from given image.
    img is path to image.
    '''
    img = cv2.imread(img)
    img = cv2.resize(img, (9,8), fx=0, fy=0, interpolation = cv2.INTER_AREA)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
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
    Two lower number represents higher similarity
    '''
    if (len(hash1) != len(hash2)):
        return None
    
    mismatches = 0
    for i in range(len(hash1)):
        if (hash1[i] != hash2[i]):
            mismatches += 1
    
    return float(mismatches) / len(hash1)

