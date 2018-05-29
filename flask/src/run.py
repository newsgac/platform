#!/usr/bin/env python

import sys
import os.path
from src.common.database import Database
DATABASE = Database()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

__author__ = 'abilgin'

if __name__ == "__main__":
    from src.app import app
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])