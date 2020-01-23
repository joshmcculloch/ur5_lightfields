#!/usr/bin/env python

import pyrealsense2 as rs
import time
from os.path import join, isdir
from os import mkdir

from RealsenseDriver import RealsenseDriver

if __name__ == "__main__":
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
	

	for i in range(1):
		rsd.save("%d" %time.time())
		time.sleep(1)



