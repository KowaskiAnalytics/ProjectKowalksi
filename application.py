## Imports
from flask import Flask, render_template, request, url_for, session, redirect
from clustercounter.clustercounter_frontend import clustercounter


## Browser session

application = Flask(__name__)
application.register_blueprint(clustercounter, url_prefix= "/clustercounter")

application.secret_key = "shhhhh"

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

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080, debug=True)