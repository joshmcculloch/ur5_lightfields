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

class RealsenseDriver(object):
	
	def __init__(self, color_path, ir1_path, ir2_path, depth_path):
		self.pipeline = rs.pipeline()
		self.config = rs.config()
		self.color_path = color_path
		self.ir1_path = ir1_path
		self.ir2_path = ir2_path
		self.depth_path = depth_path
		
		# Enable color stream at full res
		self.config.enable_stream(
			stream_type=rs.stream.color, 
			width=1920, 
			height=1080, 
			format=rs.format.rgb8, 
			framerate=30)
		
		self.config.enable_stream(
			stream_type=rs.stream.infrared,
			stream_index=1, 
			width=1280, 
			height=720, 
			format=rs.format.y8, 
			framerate=30)
			
		self.config.enable_stream(
			stream_type=rs.stream.infrared,
			stream_index=2, 
			width=1280, 
			height=720, 
			format=rs.format.y8, 
			framerate=30)
		
		self.config.enable_stream(
			stream_type=rs.stream.depth, 
			width=1280, 
			height=720, 
			format=rs.format.z16, 
			framerate=30)
		
		self.profile = self.pipeline.start(self.config)
		
		device = self.profile.get_device()
		sensors = device.query_sensors()
		for s in sensors:
			if s.is_depth_sensor():
				s.set_option(rs.option.emitter_enabled, 0)
			#print(s)
			#print(s.is_depth_sensor())
			#print(s.get_supported_options())

		print("Warming camera")
		self.warm_camera()
		print("Done")
		
		
	def warm_camera(self, sec=1.0):
		"""
		Run camera for (sec) seconds to allow auto exposure to settle.
		"""
		end_time = time.time() + sec
		while end_time > time.time():
			frames = self.pipeline.wait_for_frames()
			
	def save(self, filename):
		frames = self.pipeline.wait_for_frames()
		
		color_frame = frames.get_color_frame()
		color_image = np.asanyarray(color_frame.get_data())
		#Image.fromarray(color_image).save(join(self.color_path, filename+".png"))
		threading.Thread(target=lambda:Image.fromarray(color_image).save(join(self.color_path, filename+".jpg"), 'JPEG', quality=95)).start()
		
		ir1_frame = frames.get_infrared_frame(1)
		ir1_image = np.asanyarray(ir1_frame.get_data())
		#Image.fromarray(ir1_image).save(join(self.ir1_path, filename+".png"))
		threading.Thread(target=lambda:Image.fromarray(ir1_image).save(join(self.ir1_path, filename+".jpg"), 'JPEG', quality=95)).start()

		
		ir2_frame = frames.get_infrared_frame(2)
		ir2_image = np.asanyarray(ir2_frame.get_data())
		#Image.fromarray(ir2_image).save(join(self.ir2_path, filename+".png"))
		threading.Thread(target=lambda:Image.fromarray(ir2_image).save(join(self.ir2_path, filename+".jpg"), 'JPEG', quality=95)).start()
		
		depth_frame = frames.get_depth_frame()
		depth_image = np.asanyarray(depth_frame.get_data())
		#Image.fromarray(depth_image).save(join(self.depth_path, filename+".png"))
		threading.Thread(target=lambda:Image.fromarray(depth_image).save(join(self.depth_path, filename+".png"))).start()
		
		return Image.fromarray(ir2_image)


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

	step_size = 10
	with tqdm(total=len(list(grid_scan(1000, 200, 700, step_size, step_size, 400)))) as pbar:
		for xyz in tqdm(grid_scan(1000, 200, 700, step_size, step_size, 400)): 
			arm.go_to_location_mm(xyz)
			rsd.save("%.4d-%.4d" %(xyz[0]+500, xyz[2]))
			pbar.update(1)


