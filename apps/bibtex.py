# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse a bibtex string and load it into database"""

import sys
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.models.models import BiblioEntry, User

from apps import db


def add_bibtex_string(bibtex_str):
    """Load input bibtex string into database."""
    # parse input biblio as unicode:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.loads(bibtex_str, parser=parser)

    for bib in bib_database.entries:
        try:
            bib_entry = BiblioEntry(ID=bib.get("ID", ""),
                    ENTRYTYPE=bib.get("ENTRYTYPE", ""),
                    authors=bib.get("author", ""),
                    title=bib.get("title", ""),
                    year=bib.get("year", ""),
                    month=bib.get("month", ""),
                    publisher=bib.get("publisher", ""),
                    journal=bib.get("journal", ""),
                    school=bib.get("school", ""),
                    pdf=bib.get("pdf", ""),
                    url=bib.get("url", ""),
                    keywords=bib.get("keywords", ""))
            db.session.add(bib_entry)
            db.session.commit()
        except:
            print("Entry already in database: ", bib.get("title"))

