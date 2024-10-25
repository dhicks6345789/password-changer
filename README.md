# Password Changer

A web-based (Python / Flask) password changer utility. Allows a user (authenticated via their Google account) to change their account password. Also allows some users, depending on permissions, to change the passwords for some other users.

The backend can be modified to change passwords for other accounts at the same time, thus allowing for passwords to be kept in sync with the Google account.

## Who Is This Project For?

Password Changer is intended for installation by the systems administrator of a Google Workspace domain, for use by their users to change passwords. It was written to provide a way for users in a school to change their account passwords and for some users (teaching staff) to be able to change the passwords of some other users (pupils). This is not something for the average user to install, it won't have any functionality for changing passwords outside of system administration.

This project might be a handy starting point for anyone looking for an example single-page Flask app complete with login-with-Google functionality.

## Implementation

Password Changer is written in Python using the Flask framework. The frontend uses Bootstrap 5. It is implemented as a single-page app - there is just the one HTML page to serve.

As a Python / Flask project, it is quite simple. There is the one Python file and one HTML file, that's pretty much it. Bootstrap library files are loaded from a CDN. Login tokens are passed to the API by JavaScript, there are no cookies used.

Password Changer can, of course, be run in test mode straight from the command line. An installation script is included for Windows that installs and configures the Waitress WSGI server as a system service, hopefully meaning the project is ready to run in production situations.

Password Changer is designed to sit behind a reverse proxy server, something that handles HTTPS. This could be an instance of Apache, Nginx, Caddy or similar, or an ingress service such as Cloudflare or NGrok.

## Installation

Password Changer is intended to be run on some kind of server, although there is no specific requirement for a "server" OS, it should work on pretty much any system you can run Python on.

Clone / download the repository from Github. Change to the folder where the repository is stored.

### On Windows

Run install.bat. This should create a folder "C:\Program Files\PasswordChanger", copy the appropriate files over and set up the Waitress WSGI server as a system service that starts on boot and that can be started and stopped via the command line or Windows Task Manager.
