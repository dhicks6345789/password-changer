# Standard libraries.
import flask
import json

# Libraries for handling Google OAuth (i.e. user sign-in) authentication flow.
import google.oauth2.id_token
import google.auth.transport.requests

app = flask.Flask(__name__)
configError = ""
clientSecretData = {"web":{"client_id":""}}

# Open and read client_secret.json containing the Google authentication client secrets.
try:
  clientSecretFile = open("client_secret.json")
except OSError:
  configError = "Could not load file client_secret.json."
else:
  clientSecretData = json.load(clientSecretFile)
  clientSecretFile.close()

appData = {
  "name": "Password Changer",
  "description": "A utility to change your account password.",
  "keywords": "password, change",
  "author": "David Hicks",
  "GoogleClientID": clientSecretData["web"]["client_id"]
}

@app.route("/")
def index():
  if configError == "":
    return flask.render_template("index.html", appData=appData)
  else:
    return flask.render_template("error.html", appData=appData, errorMessage=configError)

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
        return "Error - " + repr(e)
    # At this point, we've verified the Google login token. Generate and cache a login token for our client-side code to use.
    loginToken = generateLoginToken({"emailAddress":IDInfo["email"], "loginType":"google"})
    return(loginToken)
  
if __name__ == "__main__":
  app.run(debug=True, port=8070)
