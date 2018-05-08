#!/usr/bin/env python
from src.app import app
import sys
import os.path
from src.common.database import Database
DATABASE = Database()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

__author__ = 'abilgin'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])