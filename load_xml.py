# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Add a XML file to the database."""

import sys
import xmltodict
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.models import BiblioEntry, User

from apps import db


def main():
    if len(sys.argv) < 2:
        print("Usage:\n\n$ python3 create_db.py yourfile.xml\n")
        sys.exit(-1)

    print("Init database with ", sys.argv[1])
    with open(sys.argv[1]) as xml_file:
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

if __name__ == '__main__':
    main()
