#!/bin/bash

sudo yum update -y

cd /usr/local/bin
mkdir ffmpeg
cd ffmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
#cp -a /usr/local/bin/ffmpeg/ffmpeg-6.1-amd64-static/ /usr/local/bin/ffmpeg/
sudo ln -s /usr/local/bin/ffmpeg/ffmpeg-6.1-amd64-static/ffmpeg /usr/bin/ffmpeg

sudo yum groupinstall "Development Tools" -y
sudo yum install gcc openssl-devel bzip2-devel libffi-devel -y
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz
sudo tar xzf Python-3.12.1.tgz
cd Python-3.12.1
sudo ./configure --enable-optimizations
sudo make
sudo make install
python3.12 --version
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.12 get-pip.py
pip3.12 --version
sudo apt install linux-tools-aws
pip install python-ffmpeg-video-streaming