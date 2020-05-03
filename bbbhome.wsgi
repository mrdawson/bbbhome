#! /usr/bin/python
activate_this = "/home/debian/bbbhome/venv/bin/activate_this.py"
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/bbbhome/")

load_dotenv("/var/www/html/bbbhome/.env")

from app import create_app

application = create_app()
