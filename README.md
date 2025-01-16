# Password Changer

A web-based (Python / [Flask](https://flask.palletsprojects.com/en/stable/)) password changer utility. Allows a user (authenticated via their Google account) to change their account password. Also allows some users, depending on permissions, to change the passwords for some other users.

The backend can be modified to change passwords for other accounts at the same time, thus allowing for passwords to be kept in sync with the Google account.

## Who Is This Project For?

Password Changer is intended for installation by the systems administrator of a Google Workspace domain, for use by their users to change passwords. It was written to provide a way for users in a school to change their account passwords and for some users (teaching staff) to be able to change the passwords of some other users (pupils). This is not something for the average user to install, it won't have any functionality for changing passwords outside of system administration.

This project might be a handy starting point for anyone looking for an example single-page Flask app complete with login-with-Google functionality.

## Requirements

You will need a "server" machine of some sort to run Password Changer on. This can be your own hardware on your local network or a server VM somewhere away on a hosting server. It doesn't need much by way of resources - even the smallest VM available on your service should be fine, and it can go on a VM shared with other services.

You will need to have access to the Google Workspace management console to be able to set up a Google OAuth 2 project.

How, exactly, you actually set passwords is up to you, but by default we use the excellent [GAM](https://github.com/GAM-team/GAM) project, which you will need to have set up and available on the same machine you plan to install Password Changer on.

Password Changer is designed to sit behind a reverse proxy server, something that handles HTTPS. This could be an instance of [Apache](https://httpd.apache.org/), [nginx](https://nginx.org/), [Caddy](https://caddyserver.com/) or similar, or an ingress service such as [Cloudflare Tunnel](https://www.cloudflare.com/en-gb/products/tunnel/) or [ngrok](https://ngrok.com/).

## Implementation

Password Changer is written in [Python](https://www.python.org/) using the [Flask](https://flask.palletsprojects.com/en/stable/) framework. The frontend uses [Bootstrap 5](https://getbootstrap.com/). It is implemented as a single-page app - there is just the one HTML page to serve.

As a Python / Flask project, it is quite simple. There is the one Python file and one HTML file, that's pretty much it. Bootstrap library files are loaded from a CDN. Login tokens are passed to the API by JavaScript, there are no cookies used.

Password Changer can be run in test mode straight from the command line. An installation script is included for Windows that installs and configures the Waitress WSGI server as a system service, hopefully meaning the project is ready to run in production situations.

## Installation

Password Changer is intended to be run on some kind of server, although there is no specific requirement for a "server" OS, it should work on pretty much any system you can run Python on.

You will need a working [Python](https://www.python.org/) environment on your machine. Python is included in most Linux distributions these days, and is simple enough to [install on Windows](https://www.python.org/downloads/windows/).

Note that the installation script for Password Changer sets up and runs with a Python Virtual Environment ([venv](https://docs.python.org/3/library/venv.html)), so any Python packages installed will be in their own self-contained setup and shouldn't affect (or even be seen by) the rest of your system.

Clone / download the repository from Github. Change to the folder where the repository is stored.

### On Windows

Run install.bat. This should create a folder `C:\Program Files\PasswordChanger`, copy the appropriate files over and set up the Waitress WSGI server as a system service that starts on boot and that can be started and stopped via the command line or Windows Task Manager.

If you want to run the Flask application in test / debug mode, you can go to a local command line and do:

```
cd "C:\Program Files\PasswordChanger"
cls & net stop PasswordChanger & venv\Scripts\python.exe app.py
```

### On Linux

Run install.sh.

## Additional Files / Applications

### Google Project / OAuth 2 Credentials

You will need to set up a project (or use an existing one) in the Google [Cloud Console](https://console.developers.google.com/apis). You will need to set up an OAuth 2 Client ID - see [Google's Documentation](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid) for a step-by-step guide.

Password Changer will need to be provided with a `client_secret.json` (place it in the application folder where you have Password Changer installed - `C:\Program Files\PasswordChanger` on Windows) containing a value for `{"web":{"client_id":"YOUR_ID_HERE.apps.googleusercontent.com"}}`. If you set up OAuth 2 credentials as above, the client_secret file you can download from the Google console contains the relevant value.

### Permissions / Groups

If you want some users of Password Changer to be able to change passwords for other users, you will need a `permissions.txt` file (again, just placed in the application install folder) in the following simple format:

```
u.one@example.com,u.two@example.com:groupOne,groupTwo
u.three@example.com:groupTwo
```

You will then also need a sub-folder called "groups" with files that match the names of the groups. Group files are simple lists of users, one per line. If wanted, default passwords can be included, separated from the username by a comma:

`groups/groupOne.txt`:
```
f.bloggs@example,com,HappyFish23
j.smith@example.com,FatChipmunk56
...
```

Hopefully, the above format is simple enough to either manually edit or automatically generate from whatever system you use for holding usernames. Any changes to permissions / groups should be picked up after 5 minutes - a nightly export job of users from your user database would probably be a good idea.

### Reverse Proxy / Ingress Service

Installing Password Changer will give you a Python / Flask project served by Waitress on your installation machine on port 8070 via HTTP (not HTTPS). You will need to find some way of making the application available to the wider network / Internet - importantly, that service will need to handle HTTPS. The default configuration should let only local HTTP connections through, so a reverse proxy / ingress service running on the same machine is going to be needed. This could be an instance of [Apache](https://httpd.apache.org/), [nginx](https://nginx.org/), [Caddy](https://caddyserver.com/) or similar, or an ingress service such as [Cloudflare Tunnel](https://www.cloudflare.com/en-gb/products/tunnel/) or [ngrok](https://ngrok.com/).

#### Cloudflare Tunnel

Password Changer was developed using Cloudflare Tunnel for handling HTTPS. Simply install the Cloudflare Tunnel client on your machine (the same one as Password Changer is on) and point it at `http://localhost:8070`.

## The Password Reset Mechanism

When a user starts a valid password reset operation, the server-side application takes the user ID and new password given and passes them to a separate script for each place where you want to set the password. Therefore, this utility can set the same password for the same user in multiple places at the same time - say if you have both a Google Workspace domain and a Microsoft O365 domain, this utility should be able to keep both passwords in sync.

### Google Workspace

Ensure GAM is installed and set up.

### Microsoft Entra ID

Ensure the [Microsoft Entra PowerShell](https://learn.microsoft.com/en-us/powershell/entra-powershell/installation?view=entra-powershell&tabs=powershell&pivots=windows) module is installed. Note that you will probably want to use the `-Scope AllUsers` option.

The PowerShell scripts included use an [access token](https://lazyadmin.nl/powershell/connect-mggraph/#access-token) for authenticating with the Microsoft Graph server. They expect to find the access token (copied from the "access token" tab of the [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)) in a file named "MSGraphAccessToken.txt". That access token needs to have `User.ReadWrite.All` permissions assigned from the "Modify permissions" tab.
