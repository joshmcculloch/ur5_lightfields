
import cv2
from os import listdir
from os.path import join
import math


images_extensions = set(['jpg','png','bmp'])

def map_range(value, imin, imax, tmin, tmax):
    intermediate = (value - imin) / (imax - imin)
    final = intermediate * (tmax-tmin) + tmin
    return final

class ImageMetaData(object):

    def __init__(self, path, filename):
        self.path  = path
        self.filename = filename


        self.x = float(filename[0:4])
        self.y = 0
        self.z = float(filename[5:9])

    def distance(self, x, z):
        return math.sqrt((self.x-x)**2 + (self.z-z)**2)

    def load(self):
        return cv2.imread(join(self.path, self.filename))

    def load_small(self):
        img = self.load()
        scale = 640.0 / img.shape[1]
        img = cv2.resize(img, (0,0), fx=scale, fy=scale)
        return img

class SimpleFieldViewer(object):

    def __init__(self):
        self.lf_path = "/local/jmm403/ur5/scan_1cm_close/color"
        self.metadata = self.image_metadata(self.lf_path)

        self.min_x = min([m.x for m in self.metadata])
        self.max_x = max([m.x for m in self.metadata])
        self.min_z = min([m.z for m in self.metadata])
        self.max_z = max([m.z for m in self.metadata])
        print(self.max_x,self.max_z)

        self.img = self.metadata[10].load()
        print(self.img.shape)

        cv2.namedWindow("Lightfield", cv2.WINDOW_AUTOSIZE );
        cv2.setMouseCallback("Lightfield", self.on_mouse)

    def run(self):
        while cv2.waitKey(1) < 0:
            cv2.imshow("Lightfield", self.img)

    def image_metadata(self, path):
        files = listdir(path)
        files = [ImageMetaData(path,f) for f in files if f[-3:] in images_extensions]
        return files

    def on_mouse(self, event, x, y, flag, *params):

        windowWidth=cv2.getWindowImageRect("Lightfield")[2]
        windowHeight=cv2.getWindowImageRect("Lightfield")[3]
        image_x = map_range(x,0,windowWidth, self.min_x, self.max_x)
        image_y = map_range(windowHeight-y,0,windowHeight, self.min_z, self.max_z)

        closest_image = self.metadata[0]
        distance = self.metadata[0].distance(image_x,image_y)
        for m in self.metadata:
            if m.distance(image_x,image_y) < distance:
                distance = m.distance(image_x,image_y)
                closest_image = m

        print("%4d, %4d" %(image_x,image_y),closest_image.x,closest_image.z )
        self.img = closest_image.load()

if __name__ == "__main__":
    sfv = SimpleFieldViewer()
    sfv.run()






