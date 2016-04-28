import os
basedir = os.path.abspath(os.path.dirname(__file__))


WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

DB_NAME = "app.db"
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ os.path.join(basedir, DB_NAME)

PORT = 5000
DEBUG = True

HAL_QUERY_API = "https://api.archives-ouvertes.fr/search/?q={0}~3&wt=bibtex"

