# README #

DCS for Forward Hadron Calorimeters based on HVsys hardware

### How do I get set up? ###

* Summary of set up

Get python 3.6+ running 

* Install Dependencies (sudo required)

Fedora / CentOS 7:

sudo yum install python3-devel qt5-qtbase-devel


Ubuntu:

sudo apt-get install python3-dev qt5-default


* Install python libraries

Use requirements.txt:

[python3 -m ensurepip]
python3 -m pip install pip --upgrade
python3 -m pip install -r requirements.txt


### Run! ###

Run gui: 
python3 control/gui2.py -c config/file_of_your_choice.xml


Run certain standalone worker: 
python3 lib/workers/alerter.py

Run poller (CLI utility to read/write hsvys registers):
python3 control/poller.py

All the scripts above use the config/PsdSlowControlConfig.xml 

### Contacts ###

* Repo owner or admin
opetukhov@inr.ru
https://bitbucket.org/legrus/pyslow/

