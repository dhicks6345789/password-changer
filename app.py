import flask

app = flask.Flask(__name__)

app_data = {
  "name": "Password Changer",
  "description": "For changing passwords",
  "author": "David Hicks",
  "html_title": "Password Changer",
  "project_name": "Password Changer",
  "keywords": "flask, webapp, template, basic"
}

@app.route("/")
def index():
  return flask.render_template("index.html", app_data=app_data)
  
if __name__ == "__main__":
  app.run(debug=DEVELOPMENT_ENV)
