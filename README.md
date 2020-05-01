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