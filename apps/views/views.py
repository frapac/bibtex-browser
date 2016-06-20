
import os
import requests
import time
import datetime
from sqlalchemy import or_, and_
from flask import jsonify, render_template, redirect,flash, request, url_for
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.utils import secure_filename

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bibdatabase import BibDatabase
from collections import defaultdict

from apps.models.models import *
from apps.bibtex import add_bibtex_string, add_xml_string
from apps import app, db, lm

from config import DB_NAME, HAL_QUERY_API, ALLOWED_EXTENSIONS


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
            flash("Login success")
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


@app.route("/index", methods=["GET", "POST"])
def get_index():
    # If a bibtex is being posted, process:
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            bibtexstr = file.read().decode("utf8")
            if file.filename[-4:] == ".bib":
                add_bibtex_string(bibtexstr)
            elif file.filename[-4:] == ".xml":
                add_xml_string(bibtexstr)
            flash("{} has been added to database.".format(file.filename))
            return redirect(request.url)

    # then, display page:
    form = ExtendedSearchForm()

    activity = db.session.query(Event).all()
    events = []
    # Store events in a dictionnary
    for p in activity:
        date = datetime.datetime.fromtimestamp(p.time).strftime("%d-%m-%Y %H:%M")
        events.append({"author": p.author, "article": p.article, "date": date, "type":p.event})

    num_entries = db.session.query(BiblioEntry).count()
    return render_template("index.html", title="Index", form=form, user=current_user.name, events=events[::-1], num_entries=num_entries)


@app.route('/request', methods=["POST"])
def follow_request():
    form = ExtendedSearchForm()
    if form.validate_on_submit():
        print(form.source.data)
        if form.source.data == "local":
            redirect("/biblio/search", code=307)
        elif form.source.data == "hal":
            redirect("/hal/"+form.name.data)
        else:
            flash("Not implemented yet")
    return redirect("/index")


@app.route('/biblio/search', methods=['GET', 'POST'])
@login_required
def search_biblio():
    """Search entries in biblio."""
    # Get the form corresponding to the query:
    form = ExtendedSearchForm()
    if form.validate_on_submit():
        if form.source.data == "local":
            s = "%" + form.name.data + "%"
            # Send request to database:
            bibdat = convert_rows_to_dict(db.session.query(BiblioEntry)\
                                            .filter(or_(BiblioEntry.authors.like(s),
                                                        BiblioEntry.title.like(s))))
            # Format bibdat and sort by years:
            templateVars = format_bibdatabase(bibdat)
            if len(bibdat) == 0:
                flash("No entry found")
            return render_template("references.html", **templateVars)
        elif form.source.data == "hal":
            redirect("/hal/"+form.name.data)
        else:
            flash("Not implemented yet")
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
    bibdat =  BiblioEntry.query.filter_by(ID=idx).first()
    result = bibdat.__dict__
    del result["_sa_instance_state"]
    return jsonify(result)


@app.route('/biblio/article:<string:idx>', methods=['GET'])
@login_required
def display_article(idx):
    """Return bibtex entry with id *idx*."""
    bibdat =  BiblioEntry.query.filter_by(ID=idx).first()
    try:
        keyword = (bibdat.keywords).split(",")
    except:
        keyword = ""

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
            "article": bibdat,
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
    bibdat = convert_rows_to_dict(db.session.query(BiblioEntry).all())
    years = [str(value.year) for value in db.session.query(BiblioEntry.year).distinct()]
    templateVars = format_bibdatabase(bibdat)
    years.sort()
    templateVars["years"] = years[::-1]
    return render_template("references.html", **templateVars)


@app.route('/biblio/query', methods=['GET'])
@login_required
def request_api():
    """Request given years and types"""
    # Process arguments of query:
    year = request.args.get("year")
    if year:
        query1 = [BiblioEntry.year.like(yy) for yy in year.split(":")]

    types = request.args.get("type")
    if types:
        query2 = [BiblioEntry.ENTRYTYPE.like(tt) for tt in types.split(":")]

    if year and types:
        fil = and_(or_(*query1), or_(*query2))
    elif year:
        fil = or_(*query1)
    elif types:
        fil = or_(*query2)
    rows = db.session.query(BiblioEntry).filter(fil)
    bibdat = convert_rows_to_dict(rows)
    years = [str(value.year) for value in db.session.query(BiblioEntry.year).distinct()]
    templateVars = format_bibdatabase(bibdat, type_filter=types)
    years.sort(key=lambda x:int(x))
    templateVars["years"] = years
    if year:
        templateVars["checked"] = [str(y) for y in year.split(":")]
    if types:
        templateVars["checked"].extend(types.split(":"))
    return render_template("references.html", **templateVars)


@app.route('/biblio/author=<string:auth>', methods=['GET'])
@login_required
def get_biblio_author(auth):
    """Return bibliography corresponding to given author."""
    auth = "%" + auth + "%"
    bibdat = convert_rows_to_dict(db.session.query(BiblioEntry).filter(BiblioEntry.authors.like(auth)).all())
    years = [str(value.year) for value in db.session.query(BiblioEntry.year).distinct()]
    templateVars = format_bibdatabase(bibdat)
    years.sort()
    templateVars["years"] = years[::-1]
    return render_template("references.html", **templateVars)


@app.route('/hal/<string:keywords>', methods=['GET'])
@login_required
def render_hal_biblio(keywords):
    """Send a query to HAL API and display returned bibtex entries."""
    # http://export.arxiv.org/api/query?search_query=au:%22leclere%22&sortBy=lastUpdatedDate&sortOrder=descending
    # https://api.archives-ouvertes.fr/search/?q=title_t:%22microgrid%22~3&wt=json
    # https://api.archives-ouvertes.fr/search/?q=auth_t:%22olivier%20bonin%22~3&wt=bibtex

    biblio = requests.get(HAL_QUERY_API.format(keywords)).text

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
    form = ExtendedSearchForm()
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
        if bib.get("keyword"):
            bib["keywords"] = bib.get("keyword", "").split(";")
        elif bib.get("keywords"):
            keywords = bib.get("keywords")
            keywords = keywords.replace(",", ";")
            bib["keywords"] = keywords.split(";")

    refsbyyear = []
    for year in base.keys():
        refsbyyear.append((year, base[year]))
    refsbyyear.sort(key=lambda x: x[0], reverse=True)

    # Update dictionnary to send to jinja template:
    templateVars["references"] = refsbyyear

    return templateVars


def convert_rows_to_dict(rows):
    return [row.__dict__ for row in rows]


# upload file:
# (code taken from official flask documentation)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

