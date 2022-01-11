# README #

DCS for Forward Hadron Calorimeters based on HVsys hardware

### How do I get set up? ###

* Summary of set up

Get python 3.6+ running 

* Dependencies

CentOS 7:

sudo yum install gtk3-devel python3-devel qt5-qtbase-devel

Fedora:

sudo yum install gtk3-devel python3-devel subversion python3.8 qt5-qtbase-devel

You also might need: 

sudo yum install g++ blis-devel blas-devel openblas-devel numpy lapack python3-distutils-extra

Ubuntu:

sudo apt-get install pkg-config libgtk-3-dev build-essential gcc-5

Then use requirements.txt:

python3 -m ensurepip
python3 -m pip install pip --upgrade
python3 -m pip install -r requirements.txt

### Run! ###

Run gui: 
python3 control/gui.py

Run certain standalone worker: 
python3 lib/workers/alerter.py

Run poller (CLI utility to read/write hsvys registers):
python3 control/poller.py

All the scripts above use the config/PsdSlowControlConfig.xml 

### Contacts ###

* Repo owner or admin
opetukhov@inr.ru
https://bitbucket.org/legrus/pyslow/

