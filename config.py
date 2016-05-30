import os
basedir = os.path.abspath(os.path.dirname(__file__))

# security settings:
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# database settings:
DB_NAME = "app.db"
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ os.path.join(basedir, DB_NAME)

# upload settings:
UPLOAD_FOLDER = 'static/pdf'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

PORT = 5000
DEBUG = True
TESTING = False

HAL_QUERY_API = "https://api.archives-ouvertes.fr/search/?q={0}~3&wt=bibtex"

