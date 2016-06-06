# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse a bibtex file to init the database."""

import sys
import os
import bibtexparser
import xmltodict
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from apps.models.models import BiblioEntry, User
from apps.bibtex import add_bibtex_string, add_xml_string

from apps import db


def load_bibtex_db(bibfile):
    """
    Load a bibtex.bib file in SQL database.

    :Parameters:
    ------------
    - bibfile (string)
        Name of the bibtex.bib file to load

    """
    print("Init database with ", bibfile)
    with open(bibfile) as bibtex_file:
        bibtex_str = bibtex_file.read()

    print("Parse BIBTEX file ...")
    add_bibtex_string(bibtex_str)
    print("Done")


def load_xml_db(xmlfile):
    """
    Load a bibfile.xml file in SQL database.

    :Parameters:
    ------------
    - bibfile (string)
        Name of the bibfile.xml file to load

    """
    print("Init database with ", xmlfile)
    with open(xmlfile) as xml_file:
        xml_str = xml_file.read()

    print("Write database...")
    add_xml_string(xml_str)
    print("Done")


def load_file_in_db(file_name):
    extension = file_name.split(".")[-1]

    if extension == "bib":
        load_bibtex_db(file_name)
    elif extension == "xml":
        load_xml_db(file_name)
    else:
        print("Extension must be either .bib or .xml")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:\n\n$ python3 load_bibfile.py yourbibtex.bib\n")
        sys.exit(-1)

    # Get extension of file to load:
    file_name = sys.argv[1]
    load_file_in_db(file_name)

