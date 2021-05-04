var CCcontainter = document.getElementById('clustercounter');
var PFcontainter = document.getElementById('pathfinder');
var logoorange = document.getElementById('logoorange');
var logopurple = document.getElementById('logopurple');
var backbox = document.getElementById('backbox')

var PFparams = {
    container: PFcontainter,
    renderer: 'svg',
    loop: false,
    autoplay:false,
    autoloadSegments: false,
    path: 'static/animation/pathfinder.json'
};

var CCparams = {
    container: CCcontainter,
    renderer: 'svg',
    loop: false,
    autoplay:false,
    autoloadSegments: false,
    path: "static/animation/ClusterCounter.json"
};

var logoparams = {
    container: logoorange,
    renderer: 'svg',
    loop: false,
    autoplay:false,
    autoloadSegments: false,
    path: 'static/animation/Homepagelogo.json'
};

var logopurpleparams = {
    container: logopurple,
    renderer: 'svg',
    loop: false,
    autoplay:false,
    autoloadSegments: false,
    path: 'static/animation/Homepagelogopurple.json'
};

var PFanim;
    PFanim = bodymovin.loadAnimation(PFparams);
	logoanim = bodymovin.loadAnimation(logoparams);
    PFcontainter.addEventListener("mouseenter", myScript1);
    PFcontainter.addEventListener("mouseleave", myScript2);

var CCanim;
    CCanim = bodymovin.loadAnimation(CCparams);
	logopurpleanim = bodymovin.loadAnimation(logopurpleparams);
    CCcontainter.addEventListener("mouseenter", myScript1CC);
    CCcontainter.addEventListener("mouseleave", myScript2CC);





function myScript1(){
    PFanim.setDirection(1);
	logoanim.setDirection(1);
    PFanim.play();
	logoanim.play();
	backbox.style.backgroundColor = "#D37417"
}

function myScript2(){
    PFanim.setDirection(-1);
	logoanim.setDirection(-1);
    PFanim.play();
	logoanim.play();
	backbox.style.backgroundColor = "#646161"
};

function myScript1CC(){
    CCanim.setDirection(1);
	logopurpleanim.setDirection(1);
    CCanim.play();
	logopurpleanim.play();
	backbox.style.backgroundColor = "#AE1DDC"
}

function myScript2CC(){
    CCanim.setDirection(-1);
	logopurpleanim.setDirection(-1);
    CCanim.play();
	logopurpleanim.play();
	backbox.style.backgroundColor = "#646161"
};

$("#sessionname").html("Session ID: "+ user)

$("#logout").click(function (){
    window.location.href="/logout"
})