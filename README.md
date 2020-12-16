# README #

DCS for Forward Hadron Calorimeters based on HVsys hardware

### How do I get set up? ###

* Summary of set up

Get python 3.7+ running, install prerequisites for wxpython, install wxpython and other pip modules.

* Dependencies

Get wxpython, e.g. for centos run:
yum groupinstall "Development Tools"
yum install ncurses-devel zlib-devel gtk+-devel gtk2-devel qt-devel tcl-devel tk-devel kernel-headers kernel-devel
yum install gtk3-devel python3-distutils-extra
yum install python-wxpython4

Then use requirements.txt:

python3 -m pip install -r requirements.txt

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Contacts ###

* Repo owner or admin
opetukhov@inr.ru
https://bitbucket.org/legrus/pyslow/

