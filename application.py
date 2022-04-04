## Imports
from flask import Flask, render_template, request, url_for, session, redirect
from clustercounter.clustercounter_frontend import clustercounter
import redis
from flask_session import Session
import uuid


## Browser session

application = Flask(__name__)
application.register_blueprint(clustercounter, url_prefix= "/clustercounter")

application.secret_key = "OK_This_is_EPIC"

#application.config['SESSION_TYPE'] = 'redis'
#application.config['SESSION_PERMANENT'] = False
#application.config['SESSION_USE_SIGNER'] = True
# application.config['SESSION_REDIS'] = redis.from_url('redis://pk-cache.dgyphc.0001.euc1.cache.amazonaws.com:6379')
# application.config['SESSION_REDIS'] = redis.from_url('redis:127.0.0.0:6379')

server_session = Session(application)


# Homepage

@application.route("/comingsoon", methods= ["POST","GET"])
def commingsoon():
    return render_template("K2Studio.html")

@application.route("/login", methods= ["POST","GET"])
def login():
    if request.method == "POST":
        sessionname = request.form["sessionname"]
        sessiondescription = request.form["sessiondescription"]
        session["user"] = uuid.uuid4()
        session["sessionname"] = sessionname
        session["sessiondescription"] = sessiondescription

        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("login.html")

@application.route("/")
def home():
    return render_template("K2Studio.html")
    # if "user" in session:
    #     if session["sessionname"] == "":
    #         sessionID = session["user"]
    #     else:
    #         sessionID = session["sessionname"]
    #
    #     return render_template("homepage.html", data=sessionID)
    # else:
    #     return redirect(url_for("login"))


@application.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("sessionname", None)
    session.pop("sessiondescription", None)
    return redirect(url_for("login"))
#
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080, debug=True)