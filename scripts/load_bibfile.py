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
from apps.bibtex import add_bibtex_string

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

    print("Parse XML file ...")
    # parse input biblio as unicode:
    parsed_xml = xmltodict.parse(xml_str)

    correspondance = dict(
            JournalArticle="article",
            Book="book",
            ConferenceProceedings="inproceedings",
            Report="techreport")

    print("Write database ...")
    for i, bib in enumerate(parsed_xml["b:Sources"]["b:Source"]):
        try:
            dic_author = bib["b:Author"]["b:Author"]["b:NameList"]["b:Person"]
            if isinstance(dic_author, list):
                author = ""
                for auth in dic_author:
                    author += auth["b:Last"]+", " + auth["b:First"] + " and "
                # Remove last "and":
                author = author[:-4]
            else:
                author = dic_author["b:Last"] + ", " + dic_author["b:First"]
        except KeyError:
            author = bib["b:Author"]["b:Author"].get("b:Corporate", "")

        sourcetype = bib.get("b:SourceType", "")
        try:
            entrytype = correspondance[sourcetype]
        except KeyError:
            entrytype = "misc"

        bib_entry = BiblioEntry(ID=bib.get("b:Tag", ""),
                                ENTRYTYPE=entrytype,
                                authors=author,
                                title=bib.get("b:Title", ""),
                                year=bib.get("b:Year", "1970"),
                                month=bib.get("b:Month", ""),
                                publisher=bib.get("b:Publisher", ""),
                                journal=bib.get("b:JournalName", ""))
        db.session.add(bib_entry)
    db.session.commit()
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

