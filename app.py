# Standard libraries
import os
import json
import uuid

# The Flask web application framework.
import flask

# The Flask-Caching in-memory store, used to store values (i.e. login tokens) between executions of this script.
import flask_caching

# The Flask-APSchedualr module, used for schedualing period tasks.
import flask_apscheduler

# Libraries for handling Google OAuth (i.e. user sign-in) authentication flow.
import google.oauth2.id_token
import google.auth.transport.requests

# Helper function to generate and cache a login token for a validated user.
def generateLoginToken(userData):
    loginToken = str(uuid.uuid4())
    loginTokenCache.set(loginToken, userData)
    return(loginToken)

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

# Initialize scheduler
scheduler = flask_apscheduler.APScheduler()
scheduler.init_app(app)
scheduler.start()

groups = {}
permissions = {}
configError = ""
defaultPasswords = {}
@scheduler.task("interval", id="refreshData", seconds=30, misfire_grace_time=900)
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

clientSecretData = {"web":{"client_id":""}}
# Open and read client_secret.json containing the Google authentication client secrets.
try:
    clientSecretFile = open("client_secret.json")
except OSError:
    configError = "Configuration error - Couldn't load file client_secret.json."
else:
    clientSecretData = json.load(clientSecretFile)
    clientSecretFile.close()

appData = {
    "name":"Password Changer",
    "description":"A utility to change your account password.",
    "keywords":"password, change",
    "author":"David Hicks",
    "configError":configError,
    "GoogleClientID":clientSecretData["web"]["client_id"]
}

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

# Return a list of additional users, if any, the current user can set the passwords of.
@app.route("/api/getAdditionalUsers", methods=["POST"])
def getAdditionalUsers():
    print(permissions)
    print(groups)
    loginToken = flask.request.values.get("loginToken", None)
    if loginToken == None:
        return("ERROR: Missing login token.")
    userData = loginTokenCache.get(loginToken)
    if not userData:
        return("ERROR: Invalid login token.")
    
    if userData["emailAddress"] in permissions.keys():
        result = {}
        for groupName in permissions[userData["emailAddress"]].split(","):
            for item in groups[groupName]:
                result[item] = 1
        print(result)
        return "[\"" + "\",\"".join(result.keys()) + "\"]"
    return "[]"

# Set the given user's password. Make sure the current user (which might be different) has permissions to set that password first.
@app.route("/api/setPassword", methods=["POST"])
def setPassword():
    loginToken = flask.request.values.get("loginToken", None)
    if loginToken == None:
        return("ERROR: Missing login token.")
    userData = loginTokenCache.get(loginToken)
    if not userData:
        return("ERROR: Invalid login token.")
    
    user = flask.request.values.get("user", None)
    if user == None:
        return("ERROR: Missing value: user.")
        
    newPassword = flask.request.values.get("newPassword", None)
    if newPassword == None:
        return("ERROR: Missing value: newPassword.")
        
    if user in defaultPasswords.keys():
        print("Setting password...")
        # To do: set password here.
        #if userData["emailAddress"] in permissions.keys():
    return "New password set for user: " + user

# Get the given user's default password. Make sure the current user (which might be different) has permissions to see that password first.
@app.route("/api/getDefaultPassword", methods=["POST"])
def getDefaultPassword():
    loginToken = flask.request.values.get("loginToken", None)
    if loginToken == None:
        return("ERROR: Missing login token.")
    userData = loginTokenCache.get(loginToken)
    if not userData:
        return("ERROR: Invalid login token.")
    
    user = flask.request.values.get("user", None)
    if user == None:
        return("ERROR: Missing value: user.")
        
    if user in defaultPasswords.keys():
        #if userData["emailAddress"] in permissions.keys():
        return defaultPasswords[user]
    return ""

if __name__ == "__main__":
    app.run(debug=True, port=8070, use_reloader=False)
