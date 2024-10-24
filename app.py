import flask
import json

app = flask.Flask(__name__)
configError = ""

# Open and read client_secret.json containing the Google authentication client secrets.
try:
  clientSecretFile = open("client_secret.json")
except OSError:
  configError = "ERROR: Could not load client_secret.json."
clientSecretData = json.load(clientSecretFile)
clientSecretFile.close()

app_data = {
  "name": "Password Changer",
  "description": "A utility for changing your account password",
  "author": "David Hicks",
  "html_title": "Password Changer",
  "project_name": "Password Changer",
  "keywords": "flask, webapp, template, basic"
}

@app.route("/")
def index():
  if configError = "":
    return flask.render_template("index.html", app_data=app_data)
  else:
    return flask.render_template("error.html", app_data=app_data)
  
if __name__ == "__main__":
  app.run()
