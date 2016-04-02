#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
A micro-application to display bibtex bibliography in browser.

"""

from apps import app
from config import DEBUG, PORT

if __name__ == '__main__':
    # Launch flask:
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')
