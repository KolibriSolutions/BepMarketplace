# Deploy Marketplace

## Setup gitlab/tue
  export https_proxy="proxy.tue.nl:3128"
  git config --global credential.helper store
  
setup git access tokens and login once.

## Setup sudo for django
  visudo
  Cmnd_Alias USER_SERVICES = /usr/bin/systemctl restart daphne
  django ALL=(ALL) NOPASSWD:USER_SERVICES


# Installing the marketplace
## Single sign-on
The marketplace uses the SAML single sign on system of the TU/e. This enables TU/e members to login with their TU/e credentials.
If you decide to host your own version of the Marketplace you have to change the SAML settings to that of your own organization.
For more information check the documentation of PySAML2 at ```http://pysaml-test.readthedocs.io/en/latest/```

## Installing necesarry software
1. install latest version of python3
1. ```python3 -m ensurepip```
1. ```pip install -U pip, setuptools```
1. ```pip install -r requirements.txt```

### For development
1. optionally install from requirements_development.txt

### For deployement
1. install nginx
1. ```pip install psycopg2```
1. install postgres
1. install redis
1. setup postgres database, update ```secrets.py``` with correct credentials if necessary (In the variables ```SECRET_KEY_IMPORT``` and ```DATABASE_PASSWORD_IMPORT```)
1. ```python manage.py collectstatic```
1. For Shen ring central login system support add ```SHEN_RING_CLIENT_ID``` and ```SHEN_RING_CLIENT_SECRET``` to ```secrets.py``` and add the corresponding entry in Shen.
1. For canvas integrations, add ```pylti``` config to ```secrets.py```.: 
``
PYLTI_CONFIG = {
    'consumers': {
        '<consumer key>': {
            'secret': '<secret key>'
        }
    }
}
``
. See the documentation/canvas_module_toevoegen.pdf for more information. 
1. setup redis, the default config is usually enough as long as it listens on localhost. Update settings.py if you change default settings such as port
1. setup nginx, an example nginx.conf can be found in the deployment folder
1. setup systemd, again example services and targets can be found in the deployment folder
1. if you have changed the example configs in the deployment folder make sure they are compatible with each other! (ie if you change the way daphne is served, make sure nginx sends it to the right thing)

## First time startup
1. change the contact email, name and hostname to your own at the top of the ```settings.py``` and ```settings_development.py``` files
1. ```python manage.py makemigrations < names of all apps >```
1. ```python manage.py migrate```
1. ```python manage.py createsuperuser```
1. fill in superuser credentials of your choosing
1. ```python init_populate.py --mode {production/debug depending on your setting} --create-dummy-data {if you want random data for development}```
1. browse to /two_factor/login/ and login with superuser, this bypasses the SAML SSO.
1. put your superuser account in the type3staffgroup
1. create a key at tracking->telemetrykey and put it in a ```telemetry_key.py``` file with ```API_KEY=<key>```

### For development
* for development put --settings=BepMarketplace.settings_development after each ```manage.py``` command
* to login use the url ```/two_factor/login``` to bypass the SAML SSO.

### For deployment
For managing deployment systemd scripts are provided and recommended to be used. The following instructions are for using systemd.
1. copy all systemd scripts and the nginx.conf to the correct system locations
1. start and enable nginx and redis servers
1. the following commands setup 4 http workers and 2 websockets. adjust numbers if necessary
  * ```systemctl enable httpworker@{1..4}.service```
  * ```systemctl enable websocketworker@{1..2}.service```
1. start and enable httpworker.target, websocketworker.target and daphne
1. start and enable telemetry (please note that the marketplace needs to be and a telemetry key  up for the daemon to connect)
