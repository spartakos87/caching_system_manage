#!/bin/bash
apt-get --assume-yes update
echo Update complete
apt-get -y install python3-pip
echo pip3 install
export LC_ALL=C
pip3 install Flask
pip3 install flask-restful


