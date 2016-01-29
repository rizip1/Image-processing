import os
import sys


def create_hash_structure(directory, number_of_dirs = 10):
    os.chdir(directory)

    for advertising in os.listdir(os.getcwd()):
        os.mkdir(os.path.join(advertising, advertising))
        os.chdir(advertising)
        for i in range(number_of_dirs):
            os.mkdir(os.path.join(advertising, str(i + 1)))
            os.mknod(os.path.join(advertising, str(i + 1), 'target_frame.txt'))
        os.chdir("../")


if __name__ == "__main__":
    if (len(sys.argv) > 2):
        create_hash_structure(sys.argv[1], sys.argv[2])
    else:
        create_hash_structure(sys.argv[1])

