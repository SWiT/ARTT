# ARTT
 An Augmented Reality Table Top using a projector and webcam.

Install the following packages (Ubuntu):
    sudo apt-get install git v4l2ucp  git  gcc-avr avr-libc openjdk-7-jre build-essential checkinstall cmake pkg-config yasm libtiff4-dev libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev  libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev python-dev python-numpy  libtbb-dev libqt4-dev libgtk2.0-dev libdmtx-utils libdmtx-dev blueman

Install pydmtx:
    cd ~
    git clone https://github.com/dmtx/dmtx-wrappers.git
    cd dmtx-wrappers/python
    sudo python setup.py install
