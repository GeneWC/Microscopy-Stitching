import tifffile
from tifffile import imread
import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
import zarr
from tqdm.notebook import tqdm
plt.rcParams['figure.figsize'] = [15, 15]

def read_microscopy(slide_path):
    store = imread(slide_path, aszarr=True)
    z = zarr.open(store, mode='r')
    return z

one_origin = np.uint8(np.array(read_microscopy('Bone5 Met1 1.ome-002.tiff')))
two_origin = np.uint8(np.array(read_microscopy('Image_Bone5 Met1 2 Her2-003.btf')))

# sift through the pictures to find keypoints and descriptors (THIS IS THE STEP TO OPTIMIZE!)
def sift(img):
    siftDetector= cv2.SIFT_create() # limit 1000 points
    kp, des = siftDetector.detectAndCompute(img, None)
    return kp, des

# draw the keypoints
def plot_sift(img, kp):
    tmp = img.copy()
    img = cv2.drawKeypoints(img, kp, tmp, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return img

kp_one, des_one = sift(one_origin)
kp_two, des_two = sift(two_origin)

kp_one_img = plot_sift(one_origin, kp_one)
kp_two_img = plot_sift(two_origin, kp_two)

height, width = kp_two_img.shape[:2]
kp_one_img_resized = cv2.resize(kp_one_img, (width, height))

total_kp = np.concatenate((kp_one_img_resized, kp_two_img))
plt.imshow(total_kp)
plt.show()