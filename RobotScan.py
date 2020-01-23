#!/usr/bin/env python

import pyrealsense2 as rs
import numpy as np
from PIL import Image
from PIL.ImageShow import *
import time
from os.path import join, isdir
from os import mkdir
import urx
from math import pi
from tqdm import tqdm
import threading

from RealsenseDriver import RealsenseDriver

class ArmDriver(object):
	
	def __init__(self):
		self.home_joints = np.array([-1.6317575613604944, -1.9731367270099085, 1.653226375579834, -2.802333656941549, -1.53627854982485, 0])
		self.home_location = np.array([0, 0.30, 0.70, -pi/2, 0, 0])
		
		self.acc = 0.1
		self.velo = 0.5
		self.rob = urx.Robot("192.168.1.1")
		self.rob.set_tcp((0,0,0,0,0,0))
		self.rob.set_payload(0.5, (0,0,0))
		
		self.go_home()
		
	def go_home(self):
		print("Homing by joints")
		self.rob.movej(self.home_joints, acc=self.acc, vel=self.velo)
		print("Homing by position")
		self.rob.movel(self.home_location, acc=self.acc, vel=self.velo)
		
	def go_to_location_mm(self, xyz, wait=True):
		target = self.home_location
		target[0:3] = xyz/1000
		self.rob.movel(target, acc=self.acc, vel=self.velo, wait=wait)


def grid_scan(width, bottom, top, xstep, zstep, ypos=300):
	left = True
	for z in range(top, bottom-zstep, -zstep):
		if left:
			for x in range(-width//2,width//2+xstep, xstep):
				yield np.array([x,ypos,z])
			left = False
		else:
			for x in range(width//2,-width//2-xstep, -xstep):
				yield np.array([x,ypos,z])
			left = True
			
def grid_scan_no_stop(width, bottom, top, xstep, zstep, ypos=300):
	left = True
	for z in range(top, bottom-zstep, -zstep):
		if left:
			yield np.array([-width//2, ypos,z])
			yield np.array([width//2, ypos,z])
			left = False
		else:
			yield np.array([width//2, ypos,z])
			yield np.array([-width//2, ypos,z])
			left = True


if __name__ == "__main__":
	no_arm_test = False
	base_dir = "./scan_%d" %time.time()
	color_dir = join(base_dir, "color")
	ir1_dir = join(base_dir, "ir1")
	ir2_dir = join(base_dir, "ir2")
	depth_dir = join(base_dir, "depth")
	
	
	if not isdir(base_dir):
		mkdir(base_dir)
		
	if not isdir(color_dir):
		mkdir(color_dir)
		
	if not isdir(ir1_dir):
		mkdir(ir1_dir)
		
	if not isdir(ir2_dir):
		mkdir(ir2_dir)
		
	if not isdir(depth_dir):
		mkdir(depth_dir)
		
	rsd = RealsenseDriver(color_dir, ir1_dir, ir2_dir, depth_dir)
	
	if no_arm_test:
		rsd.save("%.4d-%.4d" %(0,0))
		exit()
	
	arm = ArmDriver()
	
	
	step_size = 10 #1mm
	
	'''
	images = 0
	wait = True
	with tqdm(total=len(list(grid_scan_no_stop(1000, 200, 700, step_size, step_size, 400)))) as pbar:
		for xyz in tqdm(grid_scan_no_stop(1000, 200, 700, step_size, step_size, 400)): 
			arm.go_to_location_mm(xyz, wait=wait)
			wait = False #wait for the first move. This lets the camera get to the start without taking photos
			arm.velo = 0.05
			while True:
				p = arm.rob.getl(wait=True)
				rsd.save("%.5d-%.5d" %(p[0]*10000+5000, p[2]*10000))
				images += 1
				# keep looping until arm is within 1mm of target, then wait 0.5 sec
				if abs(p[0] - xyz[0]/1000) < 0.01 and abs(p[2] - xyz[2]/1000) < 0.01:
					time.sleep(0.5)
					break
				pbar.set_description("Images: %5d    Postion: (%4d,%4d,%4d,)" % (images,p[0]*1000,p[1]*1000,p[2]*1000))
				pbar.update(0)
			#
			pbar.update(1)'''

	step_size = 100
	with tqdm(total=len(list(grid_scan(1000, 200, 700, step_size, step_size, 400)))) as pbar:
		for xyz in tqdm(grid_scan(1000, 200, 700, step_size, step_size, 400)): 
			arm.go_to_location_mm(xyz)
			rsd.save("%.4d-%.4d" %(xyz[0]+500, xyz[2]))
			pbar.update(1)


