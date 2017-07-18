# SWiT ARTT
 https://github.com/SWiT/ARTT/

 An Augmented Reality Table Top using sanded clear acrylic, mirrors, projectors, and cameras.

TODO: Migrating to OpenCV 3.2.0 and Aruco symbols.

Install OpenCV in Ubuntu 16.04
http://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/

sudo apt-get install build-essential cmake pkg-config libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev \
    libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran \
    python2.7-dev python-numpy

git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

cd ~/opencv
git fetch origin
git checkout -b v3.3.0-rc 3.3.0-rc

cd ~/opencv_contrib
git fetch origin
git checkout -b v3.3.0-rc 3.3.0-rc

cd ~/opencv
sudo rm -R build
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D PYTHON_EXECUTABLE=/usr/bin/python2.7 \
    -D BUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ldconfig