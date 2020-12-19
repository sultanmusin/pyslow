# README #

DCS for Forward Hadron Calorimeters based on HVsys hardware

### How do I get set up? ###

* Summary of set up

Get python 3.7 running 

* Using anaconda (https://docs.anaconda.com/anaconda/install/linux/):


conda create --name dcs wxpython bs4 lxml python=3.7
conda activate dcs
pip install wxasync

Sorry, the more recent python versions (3.8+) are currently not supported due to conda conflist with wxpython (?)

Also the commands below were not tested, try them at your own risk (or just see 'Using anaconda' above)

* Dependencies

Get wxpython, e.g. for centos run:
yum groupinstall "Development Tools"
yum install ncurses-devel zlib-devel gtk+-devel gtk2-devel qt-devel tcl-devel tk-devel kernel-headers kernel-devel
yum install gtk3-devel python3-distutils-extra
yum install python-wxpython4

Then use requirements.txt:

python3 -m pip install -r requirements.txt


### Contacts ###

* Repo owner or admin
opetukhov@inr.ru
https://bitbucket.org/legrus/pyslow/

