
```
virtualenv -p python3 env
source env/bin/activate

pip install opencv-python
```

Or compile opencv

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
