#! env python3

import struct
import numpy as np

# dataset train
# dataset test

def read():
    with open('mnist/train-labels.idx1-ubyte', 'rb') as f:
        _, num = struct.unpack('>II', f.read(8))
        train_lbl = np.fromfile(f, dtype=np.int8).reshape(num)
    with open('mnist/train-images.idx3-ubyte', 'rb') as f:
        _, num, rows, cols = struct.unpack('>IIII', f.read(16))
        train_img = np.fromfile(f, dtype=np.uint8).reshape(num, rows, cols)
    with open('mnist/t10k-labels.idx1-ubyte', 'rb') as f:
        _, num = struct.unpack('>II', f.read(8))
        test_lbl = np.fromfile(f, dtype=np.int8).reshape(num)
    with open('mnist/t10k-images.idx3-ubyte', 'rb') as f:
        _, num, rows, cols = struct.unpack('>IIII', f.read(16))
        test_img = np.fromfile(f, dtype=np.uint8).reshape(num, rows, cols)
    return (train_lbl, train_img, test_lbl, test_img)

if '__main__' == __name__:
    read()