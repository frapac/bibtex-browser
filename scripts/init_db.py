
import sys
from apps import db
from apps.models import *
from load_bibfile import load_file_in_db


def main():
    db.create_all()

    if len(sys.argv) == 2:
        load_file_in_db(sys.argv[1])


if __name__ == "__main__":
    main()

