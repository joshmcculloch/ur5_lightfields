import numpy as np
from os.path import join, isdir, relpath
from os import mkdir
from PIL import Image
import json


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {"__nparray__":True, "__npdata__":obj.tolist()}
        return json.JSONEncoder.default(self, obj)

def numpy_decoder_hook(dct):
    if '__nparray__' in dct:
        return np.array(dct['__npdata__'])
    return dct

class MaaraExport(object):

    def __init__(self, base_path):
        self.base_path = base_path
        self.ir1_images = []
        self.ir2_images = []
        self.image_counter = 0
        self.ir1 = None
        self.ir2 = None
        self.l2r = None

        self.ir1_dir = join(self.base_path, "ir1")
        self.ir2_dir = join(self.base_path, "ir2")

        if not isdir( self.base_path ):
            mkdir( self.base_path )
        if not isdir( self.ir1_dir ):
            mkdir( self.ir1_dir )
        if not isdir( self.ir2_dir ):
            mkdir( self.ir2_dir )

    def set_ir1_camera(self, K, coeffs, size):
        self.ir1 = dict(K=K, dist=coeffs, dim=size)

    def set_ir2_camera(self, K, coeffs, size):
        self.ir2 = dict(K=K, dist=coeffs, dim=size)

    def set_l2r(self, location, rotation):
        self.l2r = dict(location=location, rotation=rotation)

    def save_images(self, ir1_frame, ir2_frame, pose):

        ir1_filename = join(self.ir1_dir, "%.5d.png" %self.image_counter)
        Image.fromarray(ir1_frame).save(ir1_filename)
        self.ir1_images.append(dict(image=relpath(ir1_filename, self.base_path), location=pose[:3], rotation=np.identity(3)))

        ir2_filename = join(self.ir2_dir, "%.5d.png" %self.image_counter)
        Image.fromarray(ir2_frame).save(ir2_filename)
        self.ir2_images.append(dict(image=relpath(ir2_filename, self.base_path), location=pose[:3]+self.l2r['location'], rotation=np.identity(3)))

        self.image_counter += 1

    def export_cameras(self):
        ir1 = dict(
            location=np.zeros(3),
            rotation=np.identity(3),
            views=self.ir1_images,
            K=self.ir1['K'],
            dist=self.ir1['dist'],
            master=True,
            dim=self.ir1['dim']
        )

        ir2 = dict(
            location=self.l2r['location'],
            rotation=self.l2r['rotation'],
            views=self.ir2_images,
            K=self.ir2['K'],
            dist=self.ir2['dist'],
            master=False,
            dim=self.ir2['dim']
        )
        return [ir1,ir2]

    def export_cameras_old(chunk, base_path):
        base_path = path.realpath(base_path)

        def export_camera(camera):
            image_path = path.realpath(camera.photo.path)
            common_path = os.path.commonprefix([base_path, image_path])

            assert common_path.startswith(base_path)
            rel_path = path.relpath(image_path, common_path)

            return dict(
                image = rel_path,
                location = np.array(camera.center),
                rotation = np.array(camera.transform.rotation()).reshape(3, 3)
            )

        def export_sensor(sensor):
            views = [export_camera(camera) for camera in chunk.cameras
                if camera.sensor == sensor and camera.transform is not None]

            camera = export_calibration(sensor.calibration)
            return dict(
                location=np.array(sensor.location),
                rotation=np.array(sensor.rotation).reshape(3, 3),
                views=views, K=camera['K'], dist=camera['dist'],
                master=sensor.master == sensor,
                dim = camera['dim']
            )

        return [export_sensor(sensor) for sensor in chunk.sensors]

    def save(self):
        cameras = self.export_cameras()
        np.save(self.base_path + "/export.npy", dict(master = 0, cameras=cameras))

        with open(self.base_path + "/export.json", 'w') as outfile:
            json.dump(dict(master = 0, cameras=cameras), outfile, indent=4, cls=NumpyEncoder)
