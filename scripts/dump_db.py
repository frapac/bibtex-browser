# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dump SQL database into bibtex file."""

import sys
import os
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.customization import convert_to_unicode
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps.models.models import BiblioEntry


def main():
    if len(sys.argv) < 3:
        print("Wrong number of arguments. Usage: \n")
        print("python3 dump_db.py name.db dump.bib")

    print("Dump database")
    print("Database: ", sys.argv[1])

    engine = create_engine('sqlite:///app.db')
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    db = BibDatabase()
    db.entries = []

    dbentries = session.query(BiblioEntry)
    for e in dbentries:
        db.entries.append(
            {'journal': e.journal,
             'title': e.title,
             'year': str(e.year),
             'publisher': e.publisher,
             'school': e.school,
             'ID': e.ID,
             'url': e.url,
             'author': e.authors,
             'keyword': e.keywords,
             'ENTRYTYPE': e.ENTRYTYPE}
                        )

    print("Write file on", sys.argv[2])
    writer = BibTexWriter()
    with open(sys.argv[2], 'w') as bibfile:
        bibfile.write(writer.write(db))

    session.close()
    print("Connection closed.")

if __name__ == '__main__':
    main()
