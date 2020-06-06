# bbbhome
#### Flask based web app and personal site
Hosted on a BeagleBone Black (bbb) microcomputer. The name is a relic from when I was just trying 
to control a thermostat (and other IoT style home automations) over the web with the BeagleBone's
 GPIO pins.
 
- Main
    - the publicly accessible part of the site
    - Resume
    - A permanently under construction, blog style documentation of some of my forays into 
      audio electronics restoration and construction
- Auth
    - This is just all of the user registration/login/password management stuff
- Library
    - Browse the e-book library
    - Full text search of the book metadata powered by Elasticsearch
    - Direct file download or send to devices via email
- Spellbook 
    - GPIO control from the web
- Homiechat
    - Here I'm just messing around with chat/blog style apps
    

## Server Setup Notes
OS: Debian 10 Buster

`sudo apt-get update`\
`sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3`\
`pip3 install virtualenv`\
`git clone https://github.com/mrdawson/bbbhome.git`\
Make sure the others packages listed below are also installed\
`cd bbbhome`\
Start the virtual environment\
`python3 -m virtualenv venv`\
`. venv/bin/activate`\
Install python packages form requirements.txt\
`pip install -r "requirements.txt"`\
Create a symbolic link to the www/html directory\
`sudo ln -sT ~/bbbhome /var/www/html/bbbhome`\
Start the apache server\
`sudo apachectl restart`\
logs for debugging are in \var\logs\apache2\error.log

If changes are made to the database models\
`flask db migrate -m "message"`\
`flask db upgrade` This will probably fail on the calibre metadata.db (which should be read only). Need to figure out how selectively upgrade only the site db.

#### .env file
```
export SITE_DATABASE_URI="mysql+pymysql://{username}:{password}@localhost:3306/{database-name}?charset=utf8"
export SQLALCHEMY_DATABASE_URI="sqlite:////home/debian/bbbhome/default.db"
export FLASK_APP="bbbhome.py"
export SECRET_KEY="{secret-key}"
export PLATFORM="BeagleBone Black"
export ELASTICSEARCH_URL="{elasticsearch-URL}"
export CALIBRE_DATABASE_URI="sqlite:///{path-to-calibre-library}/metadata.db"
export CALIBRE_PATH="{path-to-calibre-library}"
export MAIL_SERVER="{smtp-server-name}"
export MAIL_USERNAME="{email-address}"
export MAIL_PASSWORD="{mail-password}"
export MAIL_PORT=587
export MAIL_USE_TLS=1
export FLASK_DEBUG=0
```

#### Other python packages that should be included but are not in the requirements.txt

- rpi-ws281x==4.2.3
- RPi.GPIO==0.7.0
- bbbio==0.0.1
- Adafruit-BBIO==1.1.1
- sysv-ipc==1.0.1

## Acknowledgments
Thanks to Miguel Grinberg and his Flask Mega-Tutorial, which was the starting place for most of this.