Install Dependencies
====================

```bash
$ apt-get install postgresql
$ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
$ curl https://pyenv.run | bash
$ pyenv install 3.7.7

```

### Configure postgresql step 1: 
 - create database
 - create user with password
 - grant user privileges on database

### Configure postgresql step 2 (maybe you know more secure way): 
 - add line to pg_hba.conf: 
```
 local   traderbotbd   trader-bot    trust
```

Setup project environment
=========================

```bash
$ git clone ...
$ cd ...
$ pyenv activate trader-bot
$ pip install -r requirements.txt

```

Apply own configuration
=======================
```bash
$ nano config/.env
```

Create `.env` with your own settings (use `.env.sample` for reference)

init data
===

Init texts & currency pack & migrations

```bash
$ python manage.py migrate
$ python manage.py init
```

Run
===

Run bot with this command

```bash
$ python manage.py start_bot  # run telegram bot & jobs
```

You can put it under `screen` tool and use these commands to manage execcution:

```bash
screen -dm -S traderbot python bot_run.py  # run in background
screen -r -S traderbot  # attach to stdout
screen -S traderbot -X quit # stop bot
```
