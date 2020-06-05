# bbbhome
Beaglebone Black home automation web app and personal site

### Server Setup

- cd bbbhome
- python3 -m virtualenv venv
- . venv/bin/activate
- python setup.py install
- export FLASK_APP=bbbhome.py (PowerShell: $env:FLASK_APP = "bbbhome.py")
- flask db init
- flask db migrate -m "users table"
- flask db upgrade


### Other python packages that should be included but are not in the requirements.txt

- rpi-ws281x==4.2.3
- RPi.GPIO==0.7.0
- bbbio==0.0.1
- Adafruit-BBIO==1.1.1
- sysv-ipc==1.0.1