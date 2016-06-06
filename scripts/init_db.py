# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps import db
from apps.models.models import *
from load_bibfile import load_file_in_db



def load_admin():
    # Add admin user
    user = User(name="admin", passwd="yourpasswd")
    db.session.add(user)
    db.session.commit()


def main():
    db.create_all()
    load_admin()

    if len(sys.argv) == 2:
        load_file_in_db(sys.argv[1])


if __name__ == "__main__":
    main()

