## Imports
from flask import Flask, render_template
from clustercounter.clustercounter_frontend import clustercounter


## Browser session

application = Flask(__name__)
application.register_blueprint(clustercounter, url_prefix= "/clustercounter")

# Homepage
@application.route("/")
def homepage():
    return render_template("homepage.html")


# if __name__ == "__main__":
#     application.run(host='0.0.0.0', port=8080, debug=True)