import flask
import json

app = flask.Flask(__name__)
configError = ""

# Open and read client_secret.json containing the Google authentication client secrets.
try:
  clientSecretFile = open("client_secret.json")
except OSError:
  configError = "ERROR: Could not load client_secret.json."
else:
  clientSecretData = json.load(clientSecretFile)
  clientSecretFile.close()

appData = {
  "name": "Password Changer",
  "Google": secret
}

@app.route("/")
def index():
  if configError = "":
    return flask.render_template("index.html", appData=appData)
  else:
    return flask.render_template("error.html", errorMessage=configError)
  
if __name__ == "__main__":
  app.run()
