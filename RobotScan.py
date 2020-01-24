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
from Export import MaaraExport

class ArmDriver(object):
	
	def __init__(self):
		self.home_joints = np.array([-1.6317575613604944, -1.9731367270099085, 1.653226375579834, -2.802333656941549, -1.53627854982485, 0])
		self.home_location = np.array([0, 0.30, 0.70, -pi/2, 0, 0])
		
		self.acc = 0.3
		self.velo = 2.5
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
	arm = ArmDriver()

	maara = MaaraExport("./scan_%d" %time.time())
	rsd = RealsenseDriver()
	
	maara.set_ir1_camera(*rsd.ir1_camera_matrix())
	maara.set_ir2_camera(*rsd.ir2_camera_matrix())
	maara.set_l2r(*rsd.l2r_extrinsics())
	step_size = 100
	with tqdm(total=len(list(grid_scan(1000, 200, 200, step_size, step_size, 400)))) as pbar:
		for xyz in tqdm(grid_scan(1000, 200, 200, step_size, step_size, 400)): 
			arm.go_to_location_mm(xyz)
			color_image, ir1_image, ir2_image, depth_image = rsd.get()
			pose = arm.rob.getl(wait=True)
			maara.save_images(ir1_image, ir2_image, np.array(pose))
			
			pbar.update(1)
			
	maara.save()



