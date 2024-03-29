import cv2
import numpy as np
from matplotlib import pyplot as plt


img = cv2.imread('finger.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(img, (7, 7), 2)
h, w = img.shape[:2]

"""Morphological gradient"""

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,8))
gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
# cv2.imshow('Morphological gradient', gradient)
# cv2.waitKey()

lowerb = np.array([0, 0, 0])
upperb = np.array([15, 15, 15])
binary = cv2.inRange(gradient, lowerb, upperb)
# cv2.imshow('Binarized gradient', binary)
# cv2.waitKey()

"""Flood fill from the edges to remove edge crystals"""

for row in range(h):
    if binary[row, 0] == 255:
        cv2.floodFill(binary, None, (0, row), 0)
    if binary[row, w-1] == 255:
        cv2.floodFill(binary, None, (w-1, row), 0)

for col in range(w):
    if binary[0, col] == 255:
        cv2.floodFill(binary, None, (col, 0), 0)
    if binary[h-1, col] == 255:
        cv2.floodFill(binary, None, (col, h-1), 0)

"""Cleaning up mask"""

foreground = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
# cv2.imshow('Cleanup up crystal foreground mask', foreground)
# cv2.waitKey()

"""Creating background and unknown mask for labeling"""

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
background = cv2.dilate(foreground, kernel, iterations=3)
unknown = cv2.subtract(background, foreground)
# cv2.imshow('Background', background)
# cv2.waitKey()

"""Watershed"""

markers = cv2.connectedComponents(foreground)[1]
markers += 1  # Add one to all labels so that background is 1, not 0
markers[unknown==255] = 0  # mark the region of unknown with zero
markers = cv2.watershed(img, markers)

"""Assign the markers a hue between 0 and 179"""

hue_markers = np.uint8(179*np.float32(markers)/np.max(markers))
blank_channel = 255*np.ones((h, w), dtype=np.uint8)
marker_img = cv2.merge([hue_markers, blank_channel, blank_channel])
marker_img = cv2.cvtColor(marker_img, cv2.COLOR_HSV2BGR)
# cv2.imshow('Colored markers', marker_img)
# cv2.waitKey()

"""Label the original image with the watershed markers"""

labeled_img = img.copy()
labeled_img[markers>1] = marker_img[markers>1]  # 1 is background color
labeled_img = cv2.addWeighted(img, 0.5, labeled_img, 0.5, 0)
cv2.imshow('watershed_result.png', labeled_img)
cv2.waitKey()






