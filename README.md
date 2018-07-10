Bluebell
========

Django client for API demonstration.  Uses the PBS APIs
 * [Locator Service](http://docs.pbs.org/confluence/display/localization/Locator)
 * [TV Schedules API v2](https://projects.pbs.org/confluence/display/tvsapi/TV+Schedules+Version+2)

# Setup

### Checkout application from git
`git clone git@github.com:pbs/bluebell.git`

### setup & activate a Python 3 virtual environment
```
mkvirtualenv -p python3 bluebell
```

### Install package & dependencies
```
pip install -e .
```

### Set environment variables
```
export BLUEBELL_DEBUG=true
export TVSS_KEY=your-key-here
```

# Run Dev environment

Start the dev server by using: `python manage.py runserver`

On your host system you should be able to use http://127.0.0.1:8000/ to access bluebell
