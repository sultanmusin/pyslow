#! /bin/bash

./poller.py -c PsdSlowControlConfig.xml -a 4 -r 0x1a | grep INFO 2>&1 >> 30.txt
./poller.py -c PsdSlowControlConfig.xml -a 32 -r 0x1a | grep INFO >> 18.txt
./poller.py -c PsdSlowControlConfig.xml -a 22 -r 0x1a | grep INFO >> 13.txt
./poller.py -c PsdSlowControlConfig.xml -a 26 -r 0x1a | grep INFO >> 15.txt
./poller.py -c PsdSlowControlConfig.xml -a 50 -r 0x1a | grep INFO >> 25.txt
./poller.py -c PsdSlowControlConfig.xml -a 88 -r 0x1a | grep INFO >> 39.txt
