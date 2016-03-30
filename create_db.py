# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse a bibtex file to init the database."""

import sys
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


#TODO: create an instance with a single dict
class BiblioEntry(Base):
    __tablename__ = "Biblio"
    ID = Column(String, primary_key=True)
    ENTRYTYPE = Column(String)
    authors = Column(String)
    title = Column(String)
    year = Column(Integer)
    month = Column(String)
    publisher = Column(String)
    journal = Column(String)
    school = Column(String)
    pdf = Column(String)
    url = Column(String)
    keywords = Column(String)



def load_bibtex():
    """Load bibtex entries in memory with bibtex parser."""
    with open('bibliographie.bib') as bibtex_file:
        bibtex_str = bibtex_file.read()

    # parse input biblio as unicode:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.loads(bibtex_str, parser=parser)
    bib_database.entries.sort(key=lambda x: x['year'], reverse=True)
    return bib_database



def main():
    print("Init database with ", sys.argv[1])

    engine = create_engine('sqlite:///app.db', echo=True)
    # Create the database:
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)

    session = Session()
    with open(sys.argv[1]) as bibtex_file:
        bibtex_str = bibtex_file.read()

    print("Parse BIBTEX file ...")
    # parse input biblio as unicode:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.loads(bibtex_str, parser=parser)

    print("Write database ...")
    for bib in bib_database.entries:
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

        session.add(bib_entry)
    session.commit()

    session.close()
    print("Done")

if __name__ == '__main__':
    main()
