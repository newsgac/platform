#!/usr/bin/env python
import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.app import app

__author__ = 'abilgin'

app.run(host='0.0.0.0', debug=app.config['DEBUG'])