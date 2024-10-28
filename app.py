# Standard libraries
import os
import json
import uuid

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
    # Set values for the Flask-Caching module. Value timeout (i.e. timeout for user sessions with no activity) is 10 minutes.
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": 600,
    "CACHE_DIR": "cache",
    "SCHEDULER_API_ENABLED": False
})

# Instantiate the cache object.
loginTokenCache = flask_caching.Cache(app)

# Open and read client_secret.json containing the Google authentication client secrets.
clientSecretData = {"web":{"client_id":""}}
try:
    clientSecretFile = open("client_secret.json")
except OSError:
    configError = "Configuration error - Couldn't load file client_secret.json."
else:
    clientSecretData = json.load(clientSecretFile)
    clientSecretFile.close()

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
configError = ""
defaultPasswords = {}
@scheduler.task("interval", id="refreshData", seconds=300, misfire_grace_time=900)
def refreshData():
    global groups
    global permissions
    global configError
    global defaultPasswords
    
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



# --- Local-only helper functions. ---

# Helper function to generate and cache a login token for a validated user.
def generateLoginToken(userData):
    loginToken = str(uuid.uuid4())
    loginTokenCache.set(loginToken, userData)
    return(loginToken)

# Helper function to check a value exists in a given set of Flask values. Throws a ValueError if not.
def checkRequiredValue(theValues, theValueName):
    result = theValues.get(theValueName, None)
    if result == None:
        raise ValueError("Missing value - " + theValueName + ".")
    return result

# Helper function to check the "loginToken" value both exists and points at a valid login session. Throws a ValueError if there's a problem.
def checkLoginToken(theValues):
    loginToken = checkRequiredValue(theValues, "loginToken")
    userData = loginTokenCache.get(loginToken)
    if not userData:
        raise ValueError("Invalid login token.")
    return userData



# API functions - these are the functions that can be called by the front-end.

# This is a single-page app, any user interface changes are made via calls to the API.
@app.route("/")
def index():
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
        return "ERROR: " + repr(e)

    # At this point, we've verified the Google login token. Generate and cache a login token for our client-side code to use.
    loginToken = generateLoginToken({"emailAddress":IDInfo["email"], "loginType":"google"})
    return loginToken + "," + IDInfo["email"]

# Just checks the given loginToken, which refreshes the time-to-live value for that token.
@app.route("/api/keepAlive", methods=["POST"])
def keepAlive():
    try:
        userData = checkLoginToken(flask.request.values)
    except ValueError as e:
        return "ERROR: " + repr(e)
    return "OK"

# Return a list of additional users, if any, the current user can set the passwords of.
@app.route("/api/getAdditionalUsers", methods=["POST"])
def getAdditionalUsers():
    try:
        userData = checkLoginToken(flask.request.values)
    except ValueError as e:
        return "ERROR: " + repr(e)
    
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
        userData = checkLoginToken(flask.request.values)
        user = checkRequiredValue(flask.request.values, "user")
    except ValueError as e:
        return "ERROR: " + repr(e)
    
    if user in defaultPasswords.keys():
        #if userData["emailAddress"] in permissions.keys():
        return defaultPasswords[user]
    return ""

# Set the given user's password. Make sure the current user (which might be different) has permissions to set that password first.
@app.route("/api/setPassword", methods=["POST"])
def setPassword():
    try:
        userData = checkLoginToken(flask.request.values)
        user = checkRequiredValue(flask.request.values, "user")
        newPassword = checkRequiredValue(flask.request.values, "newPassword")
    except ValueError as e:
        return "ERROR: " + repr(e)
    
    if user in defaultPasswords.keys():
        print("Setting password...")
        # To do: set password here.
        #if userData["emailAddress"] in permissions.keys():
    return "New password set for user: " + user

if __name__ == "__main__":
    app.run(debug=True, port=8070, use_reloader=False)
