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
  print(configError)
else:
  clientSecretData = json.load(clientSecretFile)
  clientSecretFile.close()

print(clientSecretData)
print(clientSecretData["web"]["client_id"])

appData = {
  "name": "Password Changer",
  "description": "A utility to change your account password.",
  "keywords": "password, change",
  "author": "David Hicks",
  "GoogleClientID": clientSecretData["web"]["client_id"]
}
print(appData)

@app.route("/")
def index():
  print("Index called")
  print(configError)
  if configError == "":
    return flask.render_template("index.html", appData=appData)
  else:
    print("Rendering error!")
    return flask.render_template("error.html", appData=appData, errorMessage=configError)
  
if __name__ == "__main__":
  app.run(debug=False, port=8070)
