#!/bin/bash

sudo yum update -y
mkdir .aws

cd /usr/local/bin
sudo mkdir ffmpeg
cd ffmpeg
sudo wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
sudo tar -xf ffmpeg-release-amd64-static.tar.xz
sudo ln -s /usr/local/bin/ffmpeg/ffmpeg-6.1-amd64-static/ffmpeg /usr/bin/ffmpeg
sudo ln -s /usr/local/bin/ffmpeg/ffmpeg-6.1-amd64-static/ffprobe /usr/bin/ffprobe
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
pip3 install python-ffmpeg-video-streaming
pip3 install pandas
pip3 install tqdm
pip3 install boto3
cd $home