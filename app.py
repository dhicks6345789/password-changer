# Standard libraries
import os
import json
import uuid
import subprocess

# The Flask web application framework...
import flask
# ...with the Flask-Caching value store, used to login tokens...
import flask_caching
# ...and the Flask-APScheduler module, used for schedualing periodic tasks.
import flask_apscheduler

# Libraries for handling Google OAuth (i.e. user sign-in) authentication flow.
import google.oauth2.id_token
import google.auth.transport.requests

# Instantiate the Flask app, set configuration values.
app = flask.Flask(__name__)
app.config.from_mapping({
    # Set values for the Flask-Caching module. I'd use memcached as a caching backend, but that's not available on Windows.
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": "cache",
    # Value timeout (i.e. timeout for user sessions with no activity) is 10 minutes (600 seconds).
    "CACHE_DEFAULT_TIMEOUT": 600,
    # We don't want to present a user interface, we just want to run an internal periodic function.
    "SCHEDULER_API_ENABLED": False
})

# Instantiate the cache object.
loginTokenCache = flask_caching.Cache(app)

configError = ""

# Open and read client_secret.json containing the Google authentication client secrets.
clientSecretData = {"web":{"client_id":""}}
try:
    clientSecretFile = open("client_secret.json")
except OSError:
    configError = "Configuration error - Couldn't load file client_secret.json."
else:
    clientSecretData = json.load(clientSecretFile)
    clientSecretFile.close()

# Open and read validIPAddresses.txt containing a list of any valid IP addresses, if we want to limit access to just known IP addresses.
validIPAddresses = []
if os.path.isfile("permissions.txt"):
    try:
        validIPAddressesFile = open("validIPAddresses.txt")
    except OSError:
        configError = "Configuration error - Couldn't load file validIPAddresses.txt."
    else:
        for IPAddressLine in validIPAddressesFile.readlines():
            IPAddress = IPAddressLine.split(" ")[0].split("#")[0].strip()
            if not IPAddress == "":
                validIPAddresses.append(IPAddress)
        validIPAddressesFile.close()

# Application details, used to render the HTML page.
appData = {
    "name":"Password Changer",
    "description":"A utility to change your account password.",
    "keywords":"password, change",
    "author":"David Hicks",
    "GoogleClientID":clientSecretData["web"]["client_id"]
}

# Initialize the scheduler.
scheduler = flask_apscheduler.APScheduler()
scheduler.init_app(app)
scheduler.start()



# --- Periodic functions. ---

# We run the "refreshData" function periodically to check and see if any permissions / group lists have been updated.
groups = {}
permissions = {}
defaultPasswords = {}
@scheduler.task("interval", id="refreshData", seconds=300, misfire_grace_time=900)
def refreshData():
    global groups
    global permissions
    global defaultPasswords
    global configError
    
    groups = {}
    defaultPasswords = {}
    if os.path.isdir("groups"):
        for group in os.listdir("groups"):
            groupName = group.rsplit(".", 1)[0]
            groups[groupName] = []
            groupFile = open("groups" + os.sep + group)
            for groupLine in groupFile.readlines():
                groupLineSplit = groupLine.split(",")
                username = groupLineSplit[0].strip()
                groups[groupName].append(username)
                if len(groupLineSplit) > 1:
                    defaultPasswords[username] = groupLineSplit[1].strip()
            groupFile.close()

    permissions = {}
    # Open and read the permissions.txt file and any group lists found in the "groups" folder.
    if os.path.isfile("permissions.txt"):
        try:
            permissionsFile = open("permissions.txt")
        except OSError:
            configError = "Configuration error - Couldn't load file permissions.txt."
        else:
            for permissionsLine in permissionsFile.readlines():
                permissionsSplit = permissionsLine.split(":")
                for permissionsUser in permissionsSplit[0].split(","):
                    groupNames = permissionsSplit[1].strip()
                    for groupName in groupNames.split(","):
                        if not groupName.strip() in groups.keys():
                            configError = "Configuration error - User " + permissionsUser.strip() + " referenced for group " + groupName.strip() + ", but that group not listed."
                    permissions[permissionsUser.strip()] = groupNames.strip()
            permissionsFile.close()
refreshData()
appData["configError"] = configError



# --- Helper functions. ---

# Helper function to generate and cache a login token for a validated user.
def generateLoginToken(userData):
    loginToken = str(uuid.uuid4())
    loginTokenCache.set(loginToken, userData)
    return(loginToken)

# Helper function to check a value exists in a given set of Flask values. Throws a ValueError if not.
def checkRequiredValue(theValueName):
    result = flask.request.values.get(theValueName, None)
    if result == None:
        raise ValueError("Missing value - " + theValueName + ".")
    return result

# Helper function to check the IP address of the request is in the whitelist, if the whitelist is defined. Throws a ValueError if not.
def checkIPAddress():
    ipAddress = flask.request.remote_addr
    if ipAddress == "127.0.0.1":
        if "HTTP_CF_CONNECTING_IP" in flask.request.environ.keys():
            ipAddress = flask.request.environ["HTTP_CF_CONNECTING_IP"]
        else:
            raise ValueError("Configuration error - no IP address available to this application.")
    if not validIPAddresses == []:
        if not ipAddress in validIPAddresses:
            raise ValueError("Configuration error - Your IP address (" + ipAddress + ") does not have permission to access this application.")

# Helper function to check the "loginToken" value both exists and points at a valid login session. Throws a ValueError if there's a problem.
def checkLoginToken():
    checkIPAddress()
    loginToken = checkRequiredValue("loginToken")
    userData = loginTokenCache.get(loginToken)
    if not userData:
        raise ValueError("Invalid login token.")
    return userData

# Helper function to check the given current user has permissions to view / change the password for another given user. Throws a ValueError
# if the current user does not have permissions for the other given user, otherwise just returns nothing if all is okay.
def checkPermissions(theCurrentUser, theOtherUser):
    if theCurrentUser == theOtherUser:
        return
    userFound = False
    if theCurrentUser in permissions.keys():
        for group in permissions[theCurrentUser].split(","):
            if theOtherUser.strip() in groups[group.strip()]:
                userFound = True
    if not userFound:
        raise ValueError("User " + theCurrentUser + " does not have permissions for " + theOtherUser)

# Helper function to split a block of plain text into lines and put <div></div> blocks around them.
def textToHTML(theText):
    result = ""
    for textLine in theText.split("\n"):
        result = result + "<div>" + textLine + "</div>"
    return result



# --- API functions - these are the functions that can be called by the front-end. ---

# This is a single-page app, there's just the one HTML page to serve - any user interface changes are made via calls to the API.
@app.route("/")
def index():
    try:
        checkIPAddress()
    except ValueError as e:
        # Invalid request IP address.
        appData["configError"] = str(e)
    return flask.render_template("index.html", appData=appData)

# When the user completes the "Sign In With Google" workflow on the client side, this function gets called to confirm they have a valid login.
@app.route("/api/verifyGoogleIDToken", methods=["POST"])
def verifyGoogleIDToken():
    googleIDToken = flask.request.values.get("googleIDToken", None)
    try:
        # See for further details: https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
        IDInfo = google.oauth2.id_token.verify_oauth2_token(googleIDToken, google.auth.transport.requests.Request(), clientSecretData["web"]["client_id"])
        
        # If the issuer isn't Google, there's a problem.
        if IDInfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")
            
        # The aud value should match the client ID.
        if not IDInfo["aud"] == clientSecretData["web"]["client_id"]:
            raise ValueError("Mismatched client ID.")
    except ValueError as e:
        # Invalid token.
        return "ERROR: " + str(e)

    # At this point, we've verified the Google login token. Generate and cache a login token for our client-side code to use.
    loginToken = generateLoginToken({"emailAddress":IDInfo["email"], "loginType":"google"})
    return loginToken + "," + IDInfo["email"]

# Just checks the given loginToken, then refreshes the time-to-live value for that token.
@app.route("/api/keepAlive", methods=["POST"])
def keepAlive():
    try:
        userData = checkLoginToken()
    except ValueError as e:
        return "ERROR: " + str(e)
    loginTokenCache.set(flask.request.values.get("loginToken"), userData)
    return "OK"

# Return a list of additional users, if any, the current user can set the passwords of.
@app.route("/api/getAdditionalUsers", methods=["POST"])
def getAdditionalUsers():
    try:
        userData = checkLoginToken()
    except ValueError as e:
        return "ERROR: " + str(e)
    
    if userData["emailAddress"] in permissions.keys():
        result = {}
        for groupName in permissions[userData["emailAddress"]].split(","):
            for item in groups[groupName]:
                result[item] = 1
        return "[\"" + "\",\"".join(result.keys()) + "\"]"
    return "[]"

# Get the given user's default password. Make sure the current user (which might be different) has permissions to see that password first.
@app.route("/api/getDefaultPassword", methods=["POST"])
def getDefaultPassword():
    try:
        userData = checkLoginToken()
        user = checkRequiredValue("user")
        checkPermissions(userData["emailAddress"], user)
    except ValueError as e:
        return "ERROR: " + str(e)
    
    if user in defaultPasswords.keys():
        return defaultPasswords[user]
    
    return ""

# Set the given user's password. Make sure the current user (which might be different) has permissions to set that password first.
@app.route("/api/setPassword", methods=["POST"])
def setPassword():
    try:
        userData = checkLoginToken()
        user = checkRequiredValue("user")
        checkPermissions(userData["emailAddress"], user)
        newPassword = checkRequiredValue("newPassword")
    except ValueError as e:
        return "ERROR: " + str(e)

    if not (os.path.exists("change-password-enabled") or os.path.exists("change-password-background")):
        return "ERROR: Neither change-password-enabled or change-password-background folders found."

    if os.path.exists("change-password-enabled"):
        for item in os.listdir("change-password-enabled"):
            if item.endswith(".ps1"):
                result = subprocess.run(["powershell", "-file", "change-password-enabled" + os.sep + item, "-UserID", user, "-Password", newPassword], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                result = subprocess.run(["change-password-enabled" + os.sep + item, user, newPassword], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if not result.returncode == 0:
                return textToHTML("ERROR: Unable to set password for user " + user + ".\nMessage returned:\n" + result.stdout.decode("utf-8"))

    if os.path.exists("change-password-background"):
        for item in os.listdir("change-password-background"):
            if item.endswith(".ps1"):
                runProcess = subprocess.Popen(["powershell", "-file", "change-password-background" + os.sep + item, "-UserID", user, "-Password", newPassword])
            else:
                runProcess = subprocess.Popen(["change-password-background" + os.sep + item, user, newPassword])
    
    return "New password set for user: " + user + "."

if __name__ == "__main__":
    app.run(debug=True, port=8070, use_reloader=False)
