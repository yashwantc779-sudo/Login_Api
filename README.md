# Login_Api
Login API is used to authenticate users by verifying their username/email and password. The client sends login credentials to the server, the server validates the data from the database, and if the credentials are correct, it returns a success response along with an authentication token or session details
Django REST Framework (DRF) Login API Running Process
Step 1: Create Django Project

Open terminal and create a new Django project.

django-admin startproject projectname

Move inside the project folder:

cd projectname
Step 2: Create Application

Create a new app for authentication or login functionality.

python manage.py startapp account
Step 3: Install Django REST Framework

Install DRF package.

pip install djangorestframework
Step 4: Add Required Apps

Add:

rest_framework
account

inside INSTALLED_APPS in settings.py.

Step 5: Create Database Tables

Generate migration files:

python manage.py makemigrations

Apply migrations to create database tables:

python manage.py migrate
Step 6: Create Admin User

Create superuser for login testing.

python manage.py createsuperuser

Enter:

Username
Email
Password
Step 7: Create Login API

Create:

Serializer
View
URL

for handling login authentication.

Step 8: Configure URLs

Connect app URLs with the main project URLs.

Step 9: Run Server

Start Django development server.

python manage.py runserver

Server will run on:

http://127.0.0.1:8000/
Step 10: Test Login API

Use:

Postman
Thunder Client
Browser API tools

Send POST request to login endpoint with username and password.

Example endpoint:

http://127.0.0.1:8000/api/login/
Complete Login Flow
User sends username and password.
API receives request.
DRF validates input data.
Django checks credentials from database.
If credentials are correct → Login successful.
If credentials are wrong → Error response returned.

This is the complete basic DRF Login API running process.
