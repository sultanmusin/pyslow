#! /bin/bash

./poller.py -c PsdSlowControlConfig.xml -b new -a 136 -r 0x28 2>&1 | grep INFO >> 1.txt
./poller.py -c PsdSlowControlConfig.xml -b new -a 142 -r 0x28 2>&1 | grep INFO >> 4.txt
./poller.py -c PsdSlowControlConfig.xml -b new -a 150 -r 0x28 2>&1 | grep INFO >> 7.txt
./poller.py -c PsdSlowControlConfig.xml -b old -a 158 -r 0x28 2>&1 | grep INFO >> 10.txt

