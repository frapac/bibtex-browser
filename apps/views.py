
import sqlite3
import requests
import time
import datetime
from flask import jsonify, render_template, redirect,flash, request
from flask.ext.login import login_required, logout_user, login_user, current_user

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bibdatabase import BibDatabase
from collections import defaultdict

from apps.models import *
from apps import app, db, lm

from config import DB_NAME


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="Not found"), 404


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=["GET", "POST"])
def login():
    """Login to application."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            print(request.args.get("next"))
            return redirect(request.args.get('next') or "/index")
        return redirect('/login')
    return render_template('about.html', form=form, title="Log in")


@app.route('/logout')
def logout():
    """Log out from application."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect('/')


@app.route("/index")
def get_index():
    form = SearchForm()

    activity = db.session.query(Event).all()
    events = []
    # Store events in a dictionnary
    for p in activity:
        date = datetime.datetime.fromtimestamp(p.time).strftime("%d-%m-%Y %H:%M")
        events.append({"author": p.author, "article": p.article, "date": date, "type":p.event})

    num_entries = db.session.query(BiblioEntry).count()
    return render_template("index.html", title="Index", form=form, user=current_user.name, events=events, num_entries=num_entries)


@app.route('/biblio/search', methods=['GET', 'POST'])
@login_required
def search_biblio():
    """Search entries in biblio."""
    # Get the form corresponding to the query:
    form = SearchForm()
    if form.validate_on_submit():
        s = form.name.data
        # Send request to database:
        bibdat = requests_db("SELECT * FROM Biblio"
                " WHERE authors LIKE '%{}%'"
                " OR title LIKE '%{}%'".format(s, s))
        # Format bibdat and sort by years:
        templateVars = format_bibdatabase(bibdat)
        return render_template("references.html", **templateVars)
    return redirect("/biblio")


@app.route('/biblio/addentry', methods=['GET', 'POST'])
@login_required
def add_entry():
    """Add a new entry to the bibliography."""
    form = BiblioForm()
    if form.validate_on_submit():
        bib_entry = BiblioEntry(ID=form.ID.data,
                                ENTRYTYPE=form.typ.data,
                                authors=form.author.data,
                                title=form.title.data,
                                year=form.year.data,
                                school="",
                                publisher="",
                                keywords=form.keywords.data,
                                url=form.url.data,
                                journal=form.journal.data)

        db.session.add(bib_entry)
        user = current_user.name
        event = Event(author=user, article=form.ID.data, event="ADD", time=time.time())
        db.session.add(event)
        db.session.commit()
        return redirect("/biblio")
    return redirect("/biblio")


@app.route('/biblio/updateentry', methods=['GET', 'POST'])
@login_required
def update_entry():
    """Add a new entry to the bibliography."""
    form = BiblioForm()
    article_name = request.environ["HTTP_REFERER"].split(":")[-1]
    if form.validate_on_submit():
        article = BiblioEntry.query.filter_by(ID=form.ID.data).first()
        article.ID = form.ID.data
        article.ENTRYTYPE = form.typ.data
        article.authors = form.author.data
        article.title = form.title.data
        article.year = form.year.data
        article.journal = form.journal.data
        article.school = form.school.data
        article.url = form.url.data
        article.keywords = form.keywords.data
        db.session.add(article)

        user = current_user.name
        event = Event(author=user, article=form.ID.data, event="UPDATE", time=time.time())
        db.session.add(event)

        db.session.commit()
        return redirect("/biblio/article:" + article_name)
    return redirect("/biblio")


@app.route('/biblio/postcomment', methods=['GET', 'POST'])
@login_required
def post_comment():
    """Add post to article."""
    form = PostForm()
    article = request.environ["HTTP_REFERER"].split(":")[-1]
    tim = time.time()
    user = current_user.name
    post = Post(author=user, article=article, message=form.message.data, time=tim)
    db.session.add(post)

    user = current_user.name
    event = Event(author=user, article=article, event="COMMENT", time=time.time())
    db.session.add(event)
    db.session.commit()
    return redirect("/biblio/article:" + article)


@app.route('/bibtex:<string:idx>', methods=['GET'])
@login_required
def get_bibtex(idx):
    """Return bibtex entry with id *idx*."""
    bibdat = requests_db("SELECT * FROM Biblio WHERE ID=='{}'".format(idx))
    bib = BiblioEntry.query.filter_by(ID=idx).first()
    return jsonify(bibdat[0])


@app.route('/biblio/article:<string:idx>', methods=['GET'])
@login_required
def display_article(idx):
    """Return bibtex entry with id *idx*."""
    bibdat = requests_db("SELECT * FROM Biblio WHERE ID=='{}'".format(idx))

    keyword = bibdat[0].get("keywords", "").split(",")

    posts = Post.query.filter_by(article=idx).all()
    dposts = []

    # Store posts in a dictionnary
    for p in posts:
        date = datetime.datetime.fromtimestamp(p.time).strftime("%d-%m-%Y %H:%M")
        dposts.append({"author": p.author, "message": p.message, "date": date})

    templateVars = {
            "license_info": "Distributed under MIT license.",
            "title": "Article",
            "engine": "Powered by Flask",
            "article": bibdat[0],
            "keyword": keyword,
            "bibform": BiblioForm(),
            "commentform": PostForm(),
            "posts": dposts
            }

    return render_template("article.html", **templateVars)


@app.route('/biblio', methods=['GET'])
@login_required
def get_all_biblio():
    """Return all bibliography, without filters."""
    bibdat = requests_db("SELECT * FROM Biblio ORDER BY year DESC")
    years = requests_db("SELECT DISTINCT year FROM Biblio ORDER BY year DESC")
    templateVars = format_bibdatabase(bibdat)
    templateVars["years"] = [y["year"] for y in years]
    return render_template("references.html", **templateVars)


@app.route('/biblio/year=<string:year>:', methods=['GET'])
@login_required
def get_biblio_year(year):
    """Return bibliography corresponding to given year."""
    subfield = "".join("year=={} OR ".format(yy) for yy in year.split(":"))

    bibdat = requests_db("SELECT * FROM Biblio WHERE {}".format(subfield[:-3]))
    years = requests_db("SELECT DISTINCT year FROM Biblio ORDER BY year DESC")
    templateVars = format_bibdatabase(bibdat)
    templateVars["checked"] = [int(y) for y in year.split(":")]
    templateVars["years"] = [y["year"] for y in years]
    return render_template("references.html", **templateVars)


@app.route('/biblio/type=<string:types>:', methods=['GET'])
@login_required
def get_biblio_types(types):
    """Return bibliography corresponding to given type."""
    subfield = "".join("ENTRYTYPE=='{}' OR ".format(tt) for tt in types.split(":"))

    bibdat = requests_db("SELECT * FROM Biblio WHERE {}".format(subfield[:-3]))
    years = requests_db("SELECT DISTINCT year FROM Biblio ORDER BY year DESC")

    templateVars = format_bibdatabase(bibdat, type_filter=types)
    templateVars["years"] = [y["year"] for y in years]
    templateVars["checked"] = types.split(":")
    return render_template("references.html", **templateVars)


@app.route('/biblio/query', methods=['GET'])
@login_required
def request_api():
    """Request given years and types"""
    year = request.args.get("year")
    if len(year) > 0 and year[-1] == ':':
        year = year[:-1]
    types = request.args.get("type")
    field_year = "".join("year=={} OR ".format(yy) for yy in year.split(":"))
    field_type = "".join("ENTRYTYPE=='{}' OR ".format(tt) for tt in types.split(":"))

    query = "SELECT * FROM Biblio WHERE ({}) AND ({})".format(field_type[:-3], field_year[:-3])
    bibdat = requests_db(query)

    years = requests_db("SELECT DISTINCT year FROM Biblio ORDER BY year DESC")
    templateVars = format_bibdatabase(bibdat, type_filter=types)
    templateVars["checked"] = [int(y) for y in year.split(":")]
    templateVars["checked"].extend(types.split(":"))
    templateVars["years"] = [y["year"] for y in years]
    return render_template("references.html", **templateVars)


@app.route('/biblio/author=<string:auth>', methods=['GET'])
@login_required
def get_biblio_author(auth):
    """Return bibliography corresponding to given author."""
    bibdat = requests_db("SELECT * FROM Biblio WHERE authors LIKE '%{}%'".format(auth))
    years = requests_db("SELECT DISTINCT year FROM Biblio ORDER BY year DESC")

    templateVars = format_bibdatabase(bibdat, type_author=auth)
    templateVars["years"] = [y["year"] for y in years]
    return render_template("references.html", **templateVars)


@app.route('/hal/<string:keywords>', methods=['GET'])
@login_required
def render_hal_biblio(keywords):
    """Send a query to HAL API and display returned bibtex entries."""
    # http://export.arxiv.org/api/query?search_query=au:%22leclere%22&sortBy=lastUpdatedDate&sortOrder=descending
    # https://api.archives-ouvertes.fr/search/?q=title_t:%22microgrid%22~3&wt=json
    # https://api.archives-ouvertes.fr/search/?q=auth_t:%22olivier%20bonin%22~3&wt=bibtex

    # TODO: move URL in config file
    biblio = requests.get("https://api.archives-ouvertes.fr/search/?q={0}~3&wt=bibtex".format(keywords)).text

    # TODO: dry this code.
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.loads(biblio, parser=parser)

    bib_database.entries.sort(key=lambda x: x['year'], reverse=True)
    templateVars = format_bibdatabase(bib_database.entries)
    return render_template("hal.html", **templateVars)


def format_bibdatabase(bib_database, year_filter=None,
        type_filter=None, type_author=None):
    """Format bibtex database and apply specified filters.

    Parameters:
    - bib_database (bibtexparser.BibtexDatabase)
        Store all bibtex entries in a list

    - year_filter (str) - Defaut is None
        If specified, filter entries by year

    - type_filter (str) - Default is None
        If specified, filter entries by types
        (phdthesis, book, inproceedings, article)

    - type_author (str) - Default is None
        If specified, filter entries by author

    """
    form = SearchForm()
    bibform = BiblioForm()
    templateVars = {
        "license_info": "Distributed under GNU license.",
        "title": "References",
        "form": form,
        "bibform": bibform,
        "engine": "Powered by Flask",
        "years": [],
        "references": [],
        "authors": [],
        "checked": [],
        "types": ["book", "article", "phdthesis", "inproceedings", "misc", "techreport"]
        }

    base = defaultdict(list)

    # TODO: clean application of different filters:
    for bib in bib_database:

        # Preprocess different type of entries:
        if bib['ENTRYTYPE'] == "book":
            bib['origin'] = bib.get('publisher', '').replace('\&', '&amp;')
        elif bib['ENTRYTYPE'] == "article":
            bib['origin'] = bib.get('journal', '')
        elif bib['ENTRYTYPE'] == "phdthesis":
            bib['origin'] = "PhD Thesis, " + bib.get('school', '')
        elif bib['ENTRYTYPE'] == "inproceedings":
            bib['origin'] = bib.get('booktitle', '')

        base[bib['year']].append(bib)

        # process authors:
        try:
            authors = bib["authors"]
        except:
            authors = bib["author"]
            bib["authors"] = bib["author"]

        for auth in authors.split("and "):
            name = auth.split(", ")[0]
            if name not in templateVars["authors"]:
                templateVars["authors"].append(name)

        # process keywords:
        try:
            bib["keywords"] = bib.get("keyword", None).split(";")
        except Exception as e:
            pass

    refsbyyear = []
    for year in base.keys():
        refsbyyear.append((year, base[year]))
    refsbyyear.sort(key=lambda x: x[0], reverse=True)

    # Update dictionnary to send to jinja template:
    templateVars["references"] = refsbyyear

    return templateVars


def requests_db(req):
    """Send a request to the DB and return a list of dict."""
    con = sqlite3.connect(DB_NAME)
    with con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(req)

        rows = cur.fetchall()
        bibdat = []
        for row in rows:
            f = dict(zip(row.keys(), row))
            bibdat.append(f)
    return bibdat


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

