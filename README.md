# Installing BEP marketplace
## Installing necesarry software
1. install latest version of python3
1. python3 -m ensurepip
1. pip install -U pip, setuptools
1. pip install -r requirements.txt

### For development
1. optionally install from requirements_development.txt

### For deployement
1. install nginx
1. pip install psycopg2
1. install postgress
1. install redis
1. setup postgress database, update secrets.py with correct credentials if necesarry (In the variables SECRET_KEY_IMPORT and DATABASE_PASSWORD_IMPORT)
1. setup redis, the default config is usually enough as long as it listens on localhost. update settings.py if you change default settings such as port
1. python manage.py collectstatic
1. setup nginx, an example nginx.conf can be found in the deployement folder
1. setup systemd, again example services and targets can be found in the deployement folder
1. if you have changed the example configs in the deployement folder make sure they are compatible with eachother! (ie if you change the way daphne is served, make sure nginx sends it to the right thing)

## First time startup
1. python manage.py makemigrations < names of all apps >
1. python manage.py migrate
1. python manage.py createsuperuser
1. fill in superuser credentials of your choosing
1. python init_populate.py --mode {production/debug depending on your setting} --create-dummy-data {if you want random data for development}
1. browse to /admin/ and login with superuser
1. put your superuser account in the type3staffgroup

### For development
* for development put --settings=BepMarketplace.settings_development after each manage.py command

### For deployement
1. start and enable nginx and redis servers
1. the following commands setup 4 http workers and 2 websockets. adjust numbers if necesarry
  * systemctl enable httpworker@{1..4}.service
  * systemctl enable websocketworker@{1..2}.service
1. start and enable httpworker.target, websocketworker.target and daphne
