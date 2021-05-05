## Imports
from flask import Flask, render_template, request, url_for, session, redirect
from clustercounter.clustercounter_frontend import clustercounter
import redis
from flask_session import Session


## Browser session

application = Flask(__name__)
application.register_blueprint(clustercounter, url_prefix= "/clustercounter")

application.secret_key = "OK_This_is_EPIC"

application.config['SESSION_TYPE'] = 'redis'
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_USE_SIGNER'] = True
application.config['SESSION_REDIS'] = redis.from_url('pk-cache.dgyphc.0001.euc1.cache.amazonaws.com:6379')

server_session = Session(application)

# Homepage
@application.route("/login", methods= ["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form["sessionname"]
        session["user"] = user
        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("login.html")

@application.route("/")
def home():
    if "user" in session:
        user = session["user"]
        print(user)
        return render_template("homepage.html", data=user)
    else:
        return redirect(url_for("login"))


@application.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
#
# if __name__ == "__main__":
#     application.run(host='0.0.0.0', port=8080, debug=True)