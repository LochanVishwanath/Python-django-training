# DropShip

DropShip - An API Platform for DropShip Front-End.

## Steps to Setup Local Environment.


### To clone the repository 

clone the repository using any of the commands.

1. `git clone  git@git.hashedin.com:hu2k19/dropship.git` 
2. `git clone https://git.hashedin.com/hu2k19/dropship.git`


### To setup local environment dependencies

1. cd into the project using `cd dropship`
2. Install libpq-dev (for ubuntu users) using
   `sudo apt-get install libpq-dev`
3. Create `.env` file using `touch .env`
4. Copy environment variables into `.env` file.
5. Create virtual environment using `virtualenv -p python3 venv`
6. Activate virtual environment using `source venv/bin/activate`
7. Install dependencies using `pip3 install -r requirements.txt`

### To generate migrations

1. Activate virtual environment using `source venv/bin/activate`
2. Export environment variables using `export $(cat .env)`
3. Generate migration using `python manage.py makemigrations <app_name>`

### To apply the migrations

1. Activate virtual environment using `source venv/bin/activate`
2. Export environment variables using `export $(cat .env)`
3. Migrate using `python manage.py migrate`

### To create superuser

1. Activate virtual environment using `source venv/bin/activate`
2. Export environment variables using `export $(cat .env)`
3. Create super user using `python manage.py createsuperuser`

### To run the server on local

1. Activate virtual environment using `source venv/bin/activate`
2. Export environment variables using `export $(cat .env)`
3. Run server using `python manage.py runserver`
   

### To run testcases

1. Activate virtual environment using `source venv/bin/activate`
2. Export environment variables using `export $(cat .env)`
3. Run testcases using `python manage.py test`
 
### To run a particular testcase

1. Activate virtual environment using `source venv/bin/activate`
2. Export environment variables using `export $(cat .env)`
3. Run a particular testcase using `python manage.py test <folder.module.filename.Classname.specific function name> `
 

### To generate test coverage

1. Activate virtual environment using `source venv/bin/activate`
2. To generate coverage file <br>
   `coverage run --rcfile=.coveragerc manage.py test`
3. After step 2, to generate coverage report <br>
   `coverage html --rcfile=.coveragerc --omit <your_virtual_env_name>/`<br>
   It will generate coverage folder in /out

### To run pylint
1. Activate virtual environment using `source venv/bin/activate`
2. To run pylint <br>
   `pylint --load-plugins pylint_django <module1> <module2> ...`
