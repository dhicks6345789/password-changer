import flask
import json

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

@app.route("/api/authenticateGoogleCredential", methods=["POST"])
def authenticateGoogleCredential():
  aud = flask.request.values.get("aud", None)
  print(aud)
  return("authCalled")

if __name__ == "__main__":
  app.run(debug=True, port=8070)
