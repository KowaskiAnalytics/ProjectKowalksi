## Imports
from flask import Flask, render_template
from clustercounter.clustercounter_frontend import clustercounter


## Browser session

app = Flask(__name__)
app.register_blueprint(clustercounter, url_prefix= "/clustercounter")

# Homepage
@app.route("/")
def homepage():
    return render_template("homepage.html")



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
