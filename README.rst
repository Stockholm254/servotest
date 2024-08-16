======
expctl
======


Main repository for the Simon Lab experiment control.
This is the home of fronpanel as well as all experiment servers.


Description
===========

The experiment is is controled by frontpanel (src/expctl/frontpanel.py) that sends commands to the various devices called servers ((src/expctl/servers/).
The installation requirements are slightly different for either of them.
In the new version of the framework data is saved in a MongoDB database.
All that functionality is encapsuled in it's own package named "expdatabase" that is contained as a git submodule.

Installation
============

- Install Anaconda 3 to your system
- create conda environment with conda env create -n expctl3 python=3.8
- conda install numpy scipy matplotlib wxpython blosc python-blosc pymongo pillow
- pip install pyzmq pyqt pyqtgraph
- install expdatabase via:
    - git submodule update --init --recursive
    - $expctl/expdatabase> python setup.py develop
- cd ../
- $expctlpython> setup.py develop

Usage
=====

- For established servers use the shortcuts in expctl/shortcuts
- For new servers/development call them via python -m expctl.servers.XXX
- For calling server use python -m expctl.servers.servoaligner.servoserver
- To zero servo angles use  python -m expctl.servers.servoaligner.servoserver zero