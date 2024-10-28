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

Run install.bat. This should create a folder `C:\Program Files\PasswordChanger`, copy the appropriate files over and set up the Waitress WSGI server as a system service that starts on boot and that can be started and stopped via the command line or Windows Task Manager.

If you want to run the Flask application in test / debug mode, you can go to a local command line and do:

```
cd "C:\Program Files\Password Changer"
cls & net stop PasswordChanger & venv\Scripts\python.exe app.py
```

### Additional Files / Applications

You will need to set up a project (or use an existing one) in the Google [Cloud Console](https://console.developers.google.com/apis). You will need to set up an OAuth 2.0 Client ID - see [Google's Documentation](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid) for a step-by-step guide.

Password Changer will need to be provided with a `client_secret.json` (place it in the application folder where you have Password Changer installed - `C:\Program Files\PasswordChanger` on Windows) containing a value for `{"web":{"client_id":"YOUR_ID_HERE.apps.googleusercontent.com"}}`. If you set up OAuth 2.0 credentials as above, the client_secret file you can download from the Google console contains the relevant value.

If you want some users of Password Changer to be able to change passwords for other users, you will need a permissions.txt file (again, just placed in the application install folder) in the following simple format:

```
u.one@example.com,u.two@example.com:groupOne,groupTwo
u.three@example.com:groupTwo
```

You will then also need a sub-folder called "groups" with files that match the names of the groups. Goup files are simple lists of users, one per line. If wanted, default passwords can be included, separated from the username by a comma:

`groups/groupOne.txt`:
```
f.bloggs@example,com,HappyFish23
j.smith@example.com,FatChipmunk56
...
```
