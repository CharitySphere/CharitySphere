# CharitySphere

![CharitySphere Banner](./.assets/banner.png)

## 🚀 Initializing Project

### Step 0: Requirements

Make sure you have installed the following tools:

- [Git](https://git-scm.com/install/windows)
- [Python](https://www.python.org/downloads/)

### Step 1: Clone the project

```sh
git clone https://github.com/CharitySphere/CharitySphere
cd CharitySphere
```

### Step 2: Initialize Virtual Environment (Recommended)

Install Python and execute following commands:

```sh
python -m pip install virtualenv
python -m venv venv
```

### Step 3: Activate Virtual Environment

```sh
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Requirements

```sh
pip install -r requirements.txt
```

### Step 5: Migrate Database

```sh
python manage.py migrate
```

### Step 6: Create Admin Account (optional)

```sh
python manage.py createsuperuser
```

## 🏃 Running Project

Execute `runserver.bat`. <br>
Or run server manually by doing the following steps:

### Step 1: Activate Virtual Environment

Using the command based on your current shell

```sh
.\venv\Scripts\Activate.ps1
```

### Step 2: Run Server

```sh
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000) on your browser

## Command History

Starting a project

```sh
pip install Django
mkdir CharitySphere && cd CharitySphere
django-admin startproject config .
```

Setting up Git

```sh
git remote add origin git@github.com:CharitySphere/CharitySphere.git
git add .
git commit -m "init: Initialized Django"
git push -u origin master
```

Apps setup

```sh
python manage.py startapp mod_home
python manage.py startapp mod_authentication
python manage.py startapp mod_dashboard
python manage.py startapp mod_donations
python manage.py startapp mod_volunteering
python manage.py startapp mod_emergency 🟡
python manage.py startapp mod_reputation
python manage.py startapp mod_chatbot
```

Taking Schema:
```sh
sqlite3 db.sqlite3 .dump > db.sql
```
