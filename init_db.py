# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Parse a bibtex file to init the database."""

import sys
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import sqlite3


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
    con = sqlite3.connect('biblio.db')

    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS Biblio")
        cur.execute("CREATE TABLE Biblio("
                        "ENTRYTYPE TEXT,"
                        "ID TEXT,"
                        "authors TEXT,"
                        "title TEXT,"
                        "year INT,"
                        "month TEXT,"
                        "publisher TEXT,"
                        "journal TEXT,"
                        "school TEXT,"
                        "pdf TEXT,"
                        "url TEXT,"
                        "keywords TEXT)")


        with open(sys.argv[1]) as bibtex_file:
            bibtex_str = bibtex_file.read()

        print("Parse BIBTEX file ...")
        # parse input biblio as unicode:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.loads(bibtex_str, parser=parser)

        print("Write database ...")
        for bib in bib_database.entries:
            cur.execute("INSERT INTO Biblio VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   [bib.get("ENTRYTYPE", ""),
                                    bib.get("ID", ""),
                                    bib.get("author", ""),
                                    bib.get("title", ""),
                                    bib.get("year", ""),
                                    bib.get("month", ""),
                                    bib.get("publisher", ""),
                                    bib.get("journal", ""),
                                    bib.get("school", ""),
                                    bib.get("pdf", ""),
                                    bib.get("url", ""),
                                    bib.get("keywords", "")])
        con.commit()
        print("Done")

if __name__ == '__main__':
    main()
