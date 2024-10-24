# Standard libraries
import os
import json
import uuid

# The Flask web application framework.
import flask

# The Flask-Caching in-memory store, used to store values (i.e. login tokens) between executions of this script.
import flask_caching

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
    "CACHE_DIR": "cache"
})
# Instantiate the cache object.
loginTokenCache = flask_caching.Cache(app)

# Open and read client_secret.json containing the Google authentication client secrets.
configError = ""
clientSecretData = {"web":{"client_id":""}}
try:
  clientSecretFile = open("client_secret.json")
except OSError:
  configError = "Configuration error - Couldn't load file client_secret.json."
else:
  clientSecretData = json.load(clientSecretFile)
  clientSecretFile.close()

# Open and read the permissions.txt file and any group lists found in the "groups" folder.
permissions = {}
if os.path.isfile("permissions.txt"):
  try:
    permissionsFile = open("permissions.txt")
  except OSError:
    configError = "Configuration error - Couldn't load file permissions.txt."
  else:
    for permissionsLine in permissionsFile.readlines():
      permissionsSplit = permissionsLine.split(":")
      for permissionsUser in permissionsSplit[0].split(","):
        permissions[permissionsUser.strip()] = permissionsSplit[1].strip()
  permissionsFile.close()

print(permissions)

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
  return loginToken

# Return a list of additional users, if any, the current user can set the passwords of.
@app.route("/api/setPassword", methods=["POST"])
def getAdditionalUsers():
  loginToken = flask.request.values.get("loginToken", None)
  if loginToken == None:
    return("ERROR: Missing login token")
  else:
    userData = loginTokenCache.get(loginToken)
    if userData:
      print(userData)
  return "[\"j.smith\",\"f.bloggs\"]"

# Set the user's own new password.
@app.route("/api/setOwnPassword", methods=["POST"])
def setOwnPassword():
  newPassword = flask.request.values.get("newPassword", None)
  return "Setting own new password: " + newPassword

if __name__ == "__main__":
  app.run(debug=True, port=8070)
