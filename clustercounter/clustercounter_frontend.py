from flask import Blueprint, render_template, request, send_file, current_app, session, redirect, url_for
import czifile
from .clustercounter_backend import ClusterAnalysis
import os
import json

clustercounter = Blueprint("clustercounter", __name__, static_folder="static", template_folder="templates")

clusteranalysis = ClusterAnalysis()


@clustercounter.route("/")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("home.html", data=user)
    else:
        return redirect(url_for("login"))


@clustercounter.route("/support")
def support():
    return render_template("support.html")


# CZI file upload
@clustercounter.route("/uploadczi", methods=["GET", "POST"])
def uploadczi():
    if request.method == "POST" and request.files:
        file = request.files["czifile"]
        filearray = czifile.imread(file)

    return clusteranalysis.showrgbimage(file, filearray)


# View/create clusterimage (should include passing the values of radio buttons)
@clustercounter.route("/viewclusterimage/<clusterchannelindex>", methods=["GET", "POST"])
def viewclusterimage(clusterchannelindex):
    global clusteranalysis
    return clusteranalysis.showclusterchannel(clusterchannelindex)


# View/create clusterimage (should include passing the values of radio buttons)
@clustercounter.route("/viewaisimage/<aischannelindex>", methods=["GET", "POST"])
def viewaisimage(aischannelindex):
    global clusteranalysis
    return clusteranalysis.showaischannel(aischannelindex)


# View/create threshimage (should include passing the values of threshold slider)
@clustercounter.route("/viewthreshimage", methods=["GET", "POST"])
def viewthreshimage():
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    donotcreatethresh = request.args["donotcreatethresh"]
    print(threshindex)
    print(clusterchannelindex)
    global clusteranalysis
    return clusteranalysis.showthreshchannel(clusterchannelindex, threshindex, checkbox, donotcreatethresh)


@clustercounter.route("/getmanualroi", methods=["GET", "POST"])
def getmanualroi():
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    coords = request.args["coords"]
    print(threshindex)
    print(clusterchannelindex)
    coords = coords.split(",")
    coords = [int(x) for x in coords]
    print(coords)
    print(type(coords))
    global clusteranalysis
    return clusteranalysis.showcutthreshchannel(clusterchannelindex, threshindex, checkbox, coords)


@clustercounter.route("/viewroichannel", methods=["GET", "POST"])
def viewroichannel():
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    aischannelindex = request.args["aischannelindex"]
    ROIthreshindex = request.args["ROIthreshindex"]
    ROIdilateindex = request.args["ROIdilateindex"]

    global clusteranalysis
    return clusteranalysis.showroichannelcutthreshchannel(clusterchannelindex, threshindex, checkbox, aischannelindex,
                                                          ROIdilateindex, ROIthreshindex, True)


@clustercounter.route("/useroichannel", methods=["GET", "POST"])
def useroichannel():
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    aischannelindex = request.args["aischannelindex"]
    ROIthreshindex = request.args["ROIthreshindex"]
    ROIdilateindex = request.args["ROIdilateindex"]

    global clusteranalysis
    return clusteranalysis.showroichannelcutthreshchannel(clusterchannelindex, threshindex, checkbox, aischannelindex,
                                                          ROIdilateindex, ROIthreshindex, False)


@clustercounter.route("/viewbgimage", methods=["GET", "POST"])
def viewbgimage():
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    bgindex = request.args["bgindex"]
    print(threshindex)
    print(clusterchannelindex)
    global clusteranalysis
    return clusteranalysis.showbgchannel(clusterchannelindex, threshindex, checkbox, bgindex)


@clustercounter.route("/viewfgdtimage", methods=["GET", "POST"])
def viewfgdtimage():
    lastactivatedpanel = request.args["lastactivatedpanel"]
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    fgindexdtthresh = request.args["fgindexdtthresh"]
    fgindexdterosion = request.args["fgindexdterosion"]

    global clusteranalysis
    return clusteranalysis.showfgdtchannel(clusterchannelindex, threshindex, checkbox, fgindexdtthresh,
                                           fgindexdterosion)


@clustercounter.route("/viewfgmimage", methods=["GET", "POST"])
def viewfgmimage():
    lastactivatedpanel = request.args["lastactivatedpanel"]
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    minimumdistance = request.args["minimumdistance"]

    global clusteranalysis
    return clusteranalysis.showfgmchannel(clusterchannelindex, threshindex, checkbox, minimumdistance)


@clustercounter.route("/performanalysis", methods=["GET", "POST"])
def peformanalysis():
    currentactivatedpanel = request.args["currentactivatedpanel"]
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    bgindex = request.args["bgindex"]
    fgindexdtthresh = request.args["fgindexdtthresh"]
    fgindexdterosion = request.args["fgindexdterosion"]
    minimumdistance = request.args["minimumdistance"]

    global clusteranalysis
    return clusteranalysis.performanalysis(currentactivatedpanel, threshindex, clusterchannelindex, bgindex,
                                           fgindexdtthresh, fgindexdterosion, minimumdistance, checkbox, False, '')


@clustercounter.route("/performadd", methods=["GET", "POST"])
def peformanadd():
    currentactivatedpanel = request.args["currentactivatedpanel"]
    threshindex = request.args["threshindex"]
    clusterchannelindex = request.args["clusterchannelindex"]
    checkbox = request.args["checkbox"]
    bgindex = request.args["bgindex"]
    fgindexdtthresh = request.args["fgindexdtthresh"]
    fgindexdterosion = request.args["fgindexdterosion"]
    minimumdistance = request.args["minimumdistance"]
    pxµm = request.args["pxµm"]

    global clusteranalysis
    return clusteranalysis.performanalysis(currentactivatedpanel, threshindex, clusterchannelindex, bgindex,
                                           fgindexdtthresh, fgindexdterosion, minimumdistance, checkbox, True, pxµm)


@clustercounter.route("/clearresults", methods=["GET", "POST"])
def clearresults():
    global clusteranalysis
    clusteranalysis.cleardf()

    return "", 204


@clustercounter.route("/downloadresults", methods=["GET", "POST"])
def downloadresults():
    global clusteranalysis
    return clusteranalysis.downloadresults()


@clustercounter.route('/downloadzip')
def downloadzip():
    global clusteranalysis
    return clusteranalysis.downloadzip()


@clustercounter.route('/downloadguide')
def downloadguide():
    path = os.path.join(current_app.root_path, 'clustercounter/documentation')
    filename = 'ICCC_GUIDE.pdf'

    return send_file(filename_or_fp=path + "/" + filename, as_attachment=True)


@clustercounter.route('/downloadexcel')
def downloadexcel():
    path = os.path.join(current_app.root_path, 'clustercounter/documentation')
    filename = 'Excel_Template.xlsx'

    return send_file(filename_or_fp=path + "/" + filename, as_attachment=True)

@clustercounter.route('/getcurrentfilelist', methods=["GET"])
def getcurrentfilelist():
    currentfilelist = clusteranalysis.viewcurrentfileslist()
    return json.dumps(currentfilelist)

