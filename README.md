# Charity Sphere

## 🆕 Initializing Project

### Step 1: Clone the project

```sh
git clone git@github.com:charity-sphere/charity-sphere.git
```

### Step 2: Initialize Virtual Environment (Recommended)

Install Python and execute following commands:

```sh
python -m pip install virtualenv
python -m venv venv
```

### Step 3: Activate Virtual Environment

Using the command based on your current shell

```sh
# Powershell
.\ENV\Scripts\Activate.ps1
# CMD
ENV\Scripts\activate.bat
# Bash and Zsh
source ENV/bin/activate
# Fish
source ENV/bin/activate.fish
```

### Step 4: Install Requirements

```sh
pip install -r requirements.txt
```

### Step 5: Create Admin Account (optional)

```sh
python manage.py createsuperuser
```

## 🏃 Running Project

Execute `runserver.bat` if you are on Windows. <br>
Or run server manually by doing the following steps:

### Step 1: Activate Virtual Environment

Using the command based on your current shell

```sh
# CMD
ENV\Scripts\activate.bat
# Powershell
.\ENV\Scripts\Activate.ps1
# Bash and Zsh
source ENV/bin/activate
# Fish
source ENV/bin/activate.fish
```

### Step 2: Run Server

```sh
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000) on your browser

## Command History

```sh
pip install Django
mkdir charity-sphere
django-admin startproject app charity-sphere

git remote add origin git@github.com:charity-sphere/charity-sphere.git
git add .
git commit -m "init: Initialized Django"
git push -u origin master
```
