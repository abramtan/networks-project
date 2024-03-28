#!/bin/bash

sudo yum update -y
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