# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse a bibtex string and load it into database"""

import sys
import xmltodict
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
                    tag=bib.get("tag", "undefined"),
                    keywords=bib.get("keywords", ""))
            db.session.add(bib_entry)
            db.session.commit()
        except:
            print("Entry already in database: ", bib.get("title"))


def add_xml_string(xml_str):
    parsed_xml = xmltodict.parse(xml_str)

    correspondance = dict(
            JournalArticle="article",
            Book="book",
            ConferenceProceedings="inproceedings",
            Report="techreport")

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
                                tag="undefined",
                                journal=bib.get("b:JournalName", ""))
        db.session.add(bib_entry)
        try:
            db.session.commit()
        except:
            print("Entry already in database.")

