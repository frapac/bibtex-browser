#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
A micro-application to display bibtex bibliography in browser.

"""

from apps import app


if __name__ == '__main__':
    # Launch flask:
    app.run(debug=True, port=5000, host='0.0.0.0')
