## Example video of captured lightfield 
[![Example video](https://img.youtube.com/vi/Iz8IWKXsYOU/0.jpg)](https://www.youtube.com/watch?v=Iz8IWKXsYOU)

## Setting up enviroment 
> This project is being developed using python3.8. It should work with any python3. Many libraries are not available for python3.8 through pip, so there are instructions for building these libraries from source below also. It can be useful to build opencv from source anyway as there author has had issues with pip's version of opencv gui operating with ubuntu.
```
virtualenv -p python3 env
source env/bin/activate

pip install urx numpy
```

### Installing opencv
Opencv can be installed using pip. 
```
pip install opencv-python
```
Or compiled from source.
```
wget https://github.com/opencv/opencv/archive/4.2.0.zip -Oopencv-4.2.0.zip
unzip opencv-4.2.0.zip -d .
cd opencv-4.2.0/
mkdir release
cd release

# notice that in the command below,
# -D INSTALL_PYTHON_EXAMPLES=ON
# is optional.

cmake -D MAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV/local/ -D PYTHON_EXECUTABLE=$VIRTUAL_ENV/bin/python -D PYTHON_PACKAGES_PATH=$VIRTUAL_ENV/lib/python3.6/site-packages -D INSTALL_PYTHON_EXAMPLES=ON ..

make -j8
make install

#The following should output 4.2.0
python -c "import cv2; print(cv2.__version__)"
```

### Installing pyrealsense
Like opencv, pyrealsesne can be installed using pip
```
pip install pyrealsense
```

Or compiled from source.
```
git clone https://github.com/IntelRealSense/librealsense.git
mkdir librealsense/build
cd librealsense/build
cmake ../ -D BUILD_PYTHON_BINDINGS:bool=true -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV/local/ -D PYTHON_EXECUTABLE=$VIRTUAL_ENV/bin/python
make -j8
make install
export PYTHONPATH=$PYTHONPATH:$VIRTUAL_ENV/local/lib
```
