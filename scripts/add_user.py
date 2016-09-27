# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script to add a new user."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps import db
from apps.models.models import *


def main():
    # Add user
    name = input("Name: ")
    passwd = input("Password: ")
    user = User(name=name, passwd=passwd)
    db.session.add(user)
    db.session.commit()



if __name__ == "__main__":
    main()

