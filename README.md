Bluebell
========

Django client for API demonstration.  Uses the PBS APIs
 * [Locator Service](http://docs.pbs.org/confluence/display/localization/Locator)
 * [TV Schedules API v2](https://projects.pbs.org/confluence/display/tvsapi/TV+Schedules+Version+2)

# Setup

### Checkout application from git
`git clone git@github.com:pbs/bluebell.git`

### Setup and start Vagrant environment
```
cd bluebell/dev
vagrant up
vagrant ssh
```

### One more bit of config
```
pip install -r requirements.txt
```
Create a local settings file
```
vim vim bluebell/settings_local.py
```
Edit file to have
```
TVSS_KEY = '<your key here>'
```

# Run Dev environment

Make sure your vagrant is running if you haven't already by using `vagrant up`

Then ssh into the vagrant box by using `vagrant ssh`

Start the dev server by using: `python manage.py runserver 10.0.2.15:8000`

On your host system you should be able to use http://127.0.0.1:8000/ to access bluebell
