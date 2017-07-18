# SWiT ARTT
 https://github.com/SWiT/ARTT/

 An Augmented Reality Table Top using sanded clear acrylic, mirrors, projectors, and cameras.

TODO: Migrating to OpenCV 3.2.0 and Aruco symbols.

Install OpenCV in Ubuntu 16.04
http://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/

cd ~/opencv
git fetch origin
git checkout -B v3.3.0-rc origin/3.3.0-rc

cd ~/opencv_contrib
git fetch origin
git checkout -B v3.3.0-rc origin/3.3.0-rc

cd ~/opencv
sudo rm -R build
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D PYTHON_EXECUTABLE=~/.virtualenvs/cv/bin/python \
    -D BUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ldconfig