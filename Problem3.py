#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 11:58:20 2025

@author: erickduarte
"""

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

MIN_MATCH_COUNT = 10

referenceImg = cv.imread('/Users/erickduarte/Documents/Panorama/IMG_4374.png')
bImg = cv.imread('/Users/erickduarte/Documents/Panorama/IMG_4375.png')

gray1= cv.cvtColor(referenceImg,cv.COLOR_BGR2GRAY)
gray2= cv.cvtColor(bImg,cv.COLOR_BGR2GRAY)
 
sift = cv.SIFT_create()
kp1 = sift.detect(gray1,None)
kp1, des1 = sift.detectAndCompute(gray1,None)

kp2 = sift.detect(gray2,None)
kp2, des2 = sift.detectAndCompute(gray2,None)
 



# FLANN parameters
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary
 
flann = cv.FlannBasedMatcher(index_params,search_params)
 
matches = flann.knnMatch(des1,des2,k=2)
 
# store all the good matches as per Lowe's ratio test.
good = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        good.append(m)
        
if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    M, mask = cv.findHomography(dst_pts, src_pts, cv.RANSAC,5.0)
    
    matchesMask = mask.ravel().tolist()
    h, w = gray1.shape
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv.perspectiveTransform(pts,M)
    img2 = cv.polylines(gray2,[np.int32(dst)],True,255,3, cv.LINE_AA)
else:
    print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
    matchesMask = None        
 
draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)
img3 = cv.drawMatches(gray1,kp1,img2,kp2,good,None,**draw_params)
plt.imshow(img3, 'gray'),plt.show()



dst_pts = cv.warpPerspective(referenceImg, M, (referenceImg.shape[1] + bImg.shape[1], referenceImg.shape[0]))

# Blend the images
#dst_pts[0:referenceImg.shape[0], 0: referenceImg.shape[1]] = referenceImg
dst_pts[bImg.shape[0]: 0, bImg.shape[1]: 0] = bImg

# Display the result
cv.imwrite('output.jpg', dst_pts)
plt.imshow(dst_pts)
plt.show()
