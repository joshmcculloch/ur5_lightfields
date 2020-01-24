#!/usr/bin/env python

import pyrealsense2 as rs
import time
from os.path import join, isdir
from os import mkdir
import cv2
import numpy as np

def scale(image, scale):
	return cv2.resize(image, (image.shape[1]//scale, image.shape[0]//scale))

class Viewer(object):

	def __init__(self):
		cv2.namedWindow("Realsense", cv2.WINDOW_AUTOSIZE );

	def update(self,image):
		cv2.imshow("Realsense", image)

from RealsenseDriver import RealsenseDriver

if __name__ == "__main__":
	rsd = RealsenseDriver()
	print(rsd.ir1_camera_matrix())
	ir1_mat, ir1_coeffs, ir1_size = rsd.ir1_camera_matrix()
	ir2_mat, ir2_coeffs, ir2_size = rsd.ir2_camera_matrix()
	extrinsics = rsd.l2r_extrinsics()
	
	R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
		ir1_mat,
		ir1_coeffs,
		ir2_mat,
		ir2_coeffs,
		ir1_size,
		np.array(extrinsics.rotation).reshape(3,3),
		np.array(extrinsics.translation),
		flags=0)
		
	m1x, m1y = cv2.initUndistortRectifyMap( ir1_mat, ir1_coeffs, R1, P1, ir1_size, cv2.CV_32FC1)
	m2x, m2y = cv2.initUndistortRectifyMap( ir2_mat, ir2_coeffs, R2, P2, ir2_size, cv2.CV_32FC1)
		
	v = Viewer()
	
	
	laser_on = True
	block_size = 5
	rsd.set_laser(1)
	while True:
		key = cv2.waitKey(1)
		if key == 108: # letter l
			if laser_on:
				laser_on = False
				rsd.set_laser(0)
			else:
				laser_on = True
				rsd.set_laser(1)
			print("laser")
		
		elif key == 82: # up arrow
			block_size += 2
			print("block size", block_size)
			
		elif key == 84: # down arrow
			if block_size > 5:
				block_size -= 2
			print("block size", block_size)
			
		elif key > 0:
			print(key)
			break
		color_image, ir1_image, ir2_image, depth_image = rsd.get()
		
		ir1_image_sr = cv2.remap(ir1_image, m1x, m1y, cv2.INTER_CUBIC)
		ir2_image_sr = cv2.remap(ir2_image, m2x, m2y, cv2.INTER_CUBIC)
		
		#ir1_image_sr = cv2.absdiff(ir1_image_sr,ir2_image_sr)
		
		#stereo_matcher = cv2.StereoSGBM_create(0, 80, 7)
		stereo_matcher = cv2.StereoBM_create(80, block_size)
		disparity = stereo_matcher.compute(ir1_image_sr,ir2_image_sr)
		'''
		print(np.min(disparity), np.max(disparity))
		rtv, binary = cv2.threshold(disparity,2,255, cv2.THRESH_BINARY)
		print(binary)
		
		rtv, labels, stats, centroids = cv2.connectedComponentsWithStats(np.uint8(binary),4)
		print(labels.dtype)'''
		disparity = np.uint8(disparity/16)
		rtv, disparity = cv2.threshold(disparity, 30, 0, cv2.THRESH_TOZERO)
		rtv, disparity = cv2.threshold(disparity, 200, 0, cv2.THRESH_TOZERO_INV)
		
		disparity = cv2.applyColorMap(np.uint8(disparity), cv2.COLORMAP_HOT);
		

		v.update(disparity)







