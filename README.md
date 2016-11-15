# bibtex-browser
Manage your bibtex file in your browser



## Installation

This package uses python3.

We recommend an installation via `virtualenv`:

```
virtualenv -p /usr/bin/python3 bibenv

source bibenv/bin/activate
pip install -r requirements.txt

```

Once these packages are installed, you should initiate the Sqlite DB:

```
python3 scripts/init_db.py

```

And add a main user:

```
python3 scripts/add_user.py

```


## Launch

To launch the application, run in your shell:

```
python3 run.py

```

Defaults parameters can be modified in `config.py`.
