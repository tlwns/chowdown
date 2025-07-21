# DreamTeam

## Eatery Management System

## APP Demo

[App demo presentation](https://www.canva.com/design/DAGtzYHedmI/Op7Hi4dldDI65LcsnZo4qA/view?utm_content=DAGtzYHedmI&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h8d91e736d2)


## Docker Setup

If you would like to run the entire app in a docker container (recommended), simply run the commands:

> `docker compose build` (skip this step if dependencies have not changed)
>
> `docker compose up frontend` (since you are running the entire stack)

Then when you are finished, `ctrl + c` to exit out of the container (currently node ignores this, so will have to wait 10 seconds or can repeat to instantly kill).

And then remember to `docker compose down` to stop the containers.

### Running only a certain subset of the app

If you only care to run the backend, or the database, you can simply run `docker compose up backend` or `docker compose up database`. If you run the backend, it will automatically start the database too as it requires this to run. Similarly running up to frontend will run both database and backend.

#### Note on schema changes with docker

The schema will only be loaded once per volume for the database.

This means that if you change the schema, run:

> `docker compose down`
>
> `docker volume ls` to list your volumes
>
> `docker volume rm <name>` where `<name>` is the volume name ending in `db-data`
>
> `docker compose build database`

## Baremetal setups

### Frontend Development Setup

When developing, cd into frontend and make sure you have installed the packages.

> Run the command `nvm use` to automatically switch to node `v20.11.1`
>
> Then run `npm i` to install all packages

Now if you would like to run the frontend detached from backend, you can simply run `npm start`.

### Backend Development Setup

When developing, be sure the below command to create a virtual environment
`python3 -m venv env`

Open the virtual environment with `env/Script/Activate.ps1` in Windows or `source env/bin/activate` on Mac

Once opened, install all requirements with `pip3 install -r requirements.txt`

Finally, set IDE interpreter to the python executable (Either inside env/Script or env/bin)

Whenever a new dependency is installed for development, make sure to add it to `requirements.txt`

If you are <ins>running following the development setup</ins>, you can simply run `uvicorn main:app --host 0.0.0.0 --port 8080` in the `Backend` directory. This will host the backend at `localhost:8080`

### Database Development Setup

If you have recently installed postgreSQL, it's recommended to set up shortcuts in `~/.profile` for easier interaction with the shell. Use `sudo nano ~/.profile` to edit the file. Add the following code at the end of the file:

```bash
alias runpg='sudo -u postgres psql'
alias pgstart='sudo service postgresql start'
alias pgstatus='sudo service postgresql status'
alias pgstop='sudo service postgresql stop'
```

Save and restart your terminal.

In a bash terminal add your postgres credentials like so: `export DB_USER=your_database_user DB_PASSWORD=your_database_password`

**Now, onto the good bits:**

Assuming, you have PostgreSQL setup, let's begin! If not, refer [here](https://www.postgresql.org/download/).

*If you are a pro at `psycopg2`, you can run* `dropdb dream_team; createdb dream_team; python3 linker.py dream_team backend/database;` in a bash terminal and everything will be ready to go in seconds! All you need to do is make sure `psycopg2` is set up before running the commmand.

Else, let's take it slowly and break the process into three steps:

#### Setting Up Schema

In a bash terminal, start postgreSQL server by using the command `pgstart`. Continue in the bash terminal, if the database already exists, drop it with `dropdb dream_team` otherwise, create a new empty database with `createdb dream_team`. You can check this using `\l`, which lists all databases. Once done, load the database schema, saving the output in a file called log with the command `psql dream_team -f backend/database/schema.sql`. Now, to connect to the database, use `psql dream_team` \
**OR**\
From a different user profile, use `runpg` to enter the PostgreSQL shell directly. If such a database exists, use `DROP DATABASE dream_team;` otherwise create a new one using `CREATE DATABASE dream_team;`. To list all databases, use `\l`. Now let us connect to the correct database, we can do this by `\c dream_team`. To load the database schema, use `\i backend/database/schema.sql`.

#### Installing dummy data

From bash terminal, run `psql -f backend/database/data.sql` \
**OR** \
From psql terminal run `\i backend/database/data.sql`

#### Installing `psycopg2`

If it is your first time working with this package, you might need to run `sudo apt-get install libpq-dev` before doing `pip3 install -r requirements.txt` in the virtual environment. (Refer [here](#backend-development-setup))

#### Useful shortcuts for PostgreSQL shell

* `\dt`: lists all relations in the current database
* `\d <table_name>`: shows details about the specific table
* `\q`: quit `psql`
  
