#!/bin/bash
sudo apt-get update
sudo apt -y install python3-pip
pip3 install boto3
wget https://this-is-my-python.s3.amazonaws.com/demo1.py
sleep 100
python3 demo1.py