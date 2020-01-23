import pyrealsense2 as rs
import numpy as np
import threading
from os.path import join, isdir
from PIL import Image
import time

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
		
		self.pipeline_profile = self.pipeline.start(self.config)
		
		self.color_profile = self.pipeline_profile.get_stream(rs.stream.color).as_video_stream_profile()
		self.ir1_profile = self.pipeline_profile.get_stream(rs.stream.infrared, 1).as_video_stream_profile()
		self.ir2_profile = self.pipeline_profile.get_stream(rs.stream.infrared, 2).as_video_stream_profile()
		
		intrinsics = self.color_profile.get_intrinsics()
		self.save_intrinsics(intrinsics, 'color')
		
		intrinsics = self.ir1_profile.get_intrinsics()
		self.save_intrinsics(intrinsics, 'ir1')
		
		intrinsics = self.ir2_profile.get_intrinsics()
		self.save_intrinsics(intrinsics, 'ir2')
		
		l2r_extrinsics = self.ir1_profile.get_extrinsics_to(self.ir2_profile)
		
		self.device = self.pipeline_profile.get_device()
		self.sensors = self.device.query_sensors()
		for s in self.sensors:
			if s.is_depth_sensor():
				s.set_option(rs.option.emitter_enabled, 0)

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
			
	def save_intrinsics(self,intrinsics, path):
		print(path)
		print(intrinsics.fx)
		print(intrinsics.fy)
		print(intrinsics.height)
		print(intrinsics.model)
		print(intrinsics.ppx)
		print(intrinsics.ppy)
		print(intrinsics.width)
		print(intrinsics.coeffs)
			
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
