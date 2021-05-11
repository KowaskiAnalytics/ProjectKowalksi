// Some code for making a square, well, square
$(window).ready(updateWidth);
$(window).resize(updateWidth);

function updateWidth(){

    var rightsquare = $('#imageviewcontainer');
    var leftbox = $('#variable-boxes');
    var contentwindow = $('#contentwindow');

    var maxwidth = contentwindow.width() - (leftbox.width() + 30);
    var maxheight = contentwindow.height() - 20;

    var dimension = Math.min(maxwidth, maxheight);

    rightsquare.css("width", dimension);
    rightsquare.css("height", dimension);
}
var coords = [];
$(document).ready(function() {
    // Upload czi file to python backend
    $("#file_submit").click(function (event) {

        $('#open_file').addClass('processing').val('Processing');

        $('#imagetitle').html($('#hiddenfileinput').val().split('\\').pop())

        var form_data = new FormData();
        form_data.append('czifile', $('#hiddenfileinput').prop('files')[0]);

        $(function () {
            $.ajax({
                type: 'POST',
                url: '/clustercounter/uploadczi',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function (data) {
                    $('#open_file').removeClass('processing').addClass('active').val('Success')
                    setTimeout(function () {
                        $('#open_file').removeClass('active').val("Open File");
                    }, 4000)
                    document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ data;
                }


            });
        });
    });

    // View the clusterimage
    $('#view_image_button_Cluster').click(function(){

        var clusterchannelindex = $('input[name="myRadio"]:checked').val();

        $.ajax({
            url: '/clustercounter/viewclusterimage/'+clusterchannelindex,
            type: 'POST',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })

    // View the clusterimage
    $('#view_image_button_AIS').click(function(){

        var aischannelindex = $('input[name="myAIS"]:checked').val();

        $.ajax({
            url: '/clustercounter/viewaisimage/'+aischannelindex,
            type: 'POST',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    // View the thresholdimage
    $('#view_image_button_thresh').click(function(){
        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var donotcreatethresh = '0'
        console.log(threshindex)
        console.log(clusterchannelindex)

        $.ajax({
            url: '/clustercounter/viewthreshimage',
            data: {threshindex:threshindex, clusterchannelindex:clusterchannelindex, checkbox:checkbox, donotcreatethresh:donotcreatethresh},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    // initiate manual ROI select
    $('#ManualROIButton').click(function () {
        $('#ROIpanel1').slideDown(300, function () {
            $(this).addClass('active');
        });
        $('#ManualROIButton').addClass('active');

        if ($('#threshcheck').is(":checked")) {
            var checkbox = '1';
        } else {
            var checkbox = '0';
        }
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var donotcreatethresh = '1'
        var analysisoption = $('input[name="myAN"]:checked').val();
        coords = []
        console.log(threshindex);
        console.log(clusterchannelindex);

        $.ajax({
            url: '/clustercounter/viewthreshimage',
            data: {
                threshindex: threshindex,
                clusterchannelindex: clusterchannelindex,
                checkbox: checkbox,
                donotcreatethresh: donotcreatethresh,
                analysisoption: analysisoption
            },
            type: 'GET',
            contentType: "image/jpeg",
            success: function (result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,' + result;
            }
        });
    })
    $('#selectedimg').on("click", function (e) {
        var $img = $(this);
        var currentClickPosX = e.pageX - $img.offset().left;
        var currentClickPosY = e.pageY - $img.offset().top;

        var currentWidth = $img.width();
        var currentHeight = $img.height();

        var naturalWidth = this.naturalWidth;
        var naturalHeight = this.naturalHeight;
        var naturalClickPosX = ((naturalWidth / currentWidth) * currentClickPosX).toFixed(0);
        var naturalClickPosY = ((naturalHeight / currentHeight) * currentClickPosY).toFixed(0);

        if($('#ManualROIButton').hasClass("active")) {
            coords.push([naturalClickPosX, naturalClickPosY]);

            $("body").append(
            $('<div class="ROIdots"></div>').css({
                position: 'absolute',
                top: e.pageY + 'px',
                left: e.pageX + 'px',
                width: '5px',
                height: '5px',
                borderRadius:'50%',
                background: 'rgba(76, 36, 115)',
            })
            );
        }
    });
    $('#submitROIbutton').on('click', function(){
        $('div.ROIdots').remove();
        $('#ManualROIButton').removeClass('active');
        $('#ROIpanel1').slideUp(300, function() {
                $(this).removeClass('active') });

        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var analysisoption = $('input[name="myAN"]:checked').val();
        coords = coords + "";

        $.ajax({
            url: '/clustercounter/getmanualroi',
            data: {threshindex:threshindex, clusterchannelindex:clusterchannelindex, coords:coords, checkbox:checkbox, analysisoption:analysisoption},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
                $('#ManualROIButton').addClass('success')
                setTimeout(function () {
                    $('#ManualROIButton').removeClass('success');
                }, 4000);
            }
        });
    });
    $('#ROIChannelButton').click(function(){
        $('#ROIpanel2').slideDown(300, function() {
                $(this).addClass('active');
            });
        $('#ROIChannelButton').addClass('active');

        var aischannelindex = $('input[name="myAIS"]:checked').val();

        $.ajax({
            url: '/clustercounter/viewaisimage/'+aischannelindex,
            type: 'POST',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    $('#view_image_button_roi').click(function(){
        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var aischannelindex = $('input[name="myAIS"]:checked').val();
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var ROIthreshindex = $('#ROIthresholdslider').val();
        var ROIdilateindex = $("#ROIdilateindex").val();
        var ROIgaussianindex = $("#ROIgaussianindex").val();
        var analysisoption = $('input[name="myAN"]:checked').val();

        $.ajax({
            url: '/clustercounter/viewroichannel',
            data: {aischannelindex:aischannelindex, clusterchannelindex:clusterchannelindex, threshindex:threshindex,
                ROIthreshindex:ROIthreshindex, ROIdilateindex:ROIdilateindex, checkbox:checkbox, analysisoption:analysisoption,
                ROIgaussianindex:ROIgaussianindex},
            type: 'GET',
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    });
    $('#submitROIbutton2').click(function(){
        $('#ROIpanel2').slideUp(300, function() {
                $(this).removeClass('active');
            });

        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var aischannelindex = $('input[name="myAIS"]:checked').val();
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var ROIthreshindex = $('#ROIthresholdslider').val();
        var ROIdilateindex = $("#ROIdilateindex").val();
        var analysisoption = $('input[name="myAN"]:checked').val();
        var ROIgaussianindex = $("#ROIgaussianindex").val();

        $.ajax({
            url: '/clustercounter/useroichannel',
            data: {aischannelindex:aischannelindex, clusterchannelindex:clusterchannelindex, threshindex:threshindex,
                ROIthreshindex:ROIthreshindex, ROIdilateindex:ROIdilateindex, checkbox:checkbox, analysisoption:analysisoption,
                ROIgaussianindex:ROIgaussianindex},
            type: 'GET',
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
                $('#ROIChannelButton').removeClass('active')
                $('#ROIChannelButton').addClass('success')
                    setTimeout(function () {
                        $('#ROIChannelButton').removeClass('success');
                    }, 4000);
            }
        })
    });
    $('#view_image_button_bg').click(function(){

        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var bgindex = $('#bgindex').val();
        console.log(threshindex)
        console.log(clusterchannelindex)

        $.ajax({
            url: '/clustercounter/viewbgimage',
            data: {threshindex:threshindex, clusterchannelindex:clusterchannelindex, bgindex:bgindex, checkbox:checkbox},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    $('#view_image_button_fg_dt').click(function(){

        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var lastactivatedpanel = '1'
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var fgindexdtthresh = $('#disttransthresh').val();
        var fgindexdterosion = $('#disttranserosion').val();

        $.ajax({
            url: '/clustercounter/viewfgdtimage',
            data: {lastactivatedpanel:lastactivatedpanel, threshindex:threshindex, clusterchannelindex:clusterchannelindex,
                fgindexdtthresh:fgindexdtthresh, fgindexdterosion:fgindexdterosion, checkbox:checkbox},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    $('#view_image_button_fg_m').click(function(){

        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var lastactivatedpanel = '2'
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var minimumdistance = $('#minimumdistance').val();

        $.ajax({
            url: '/clustercounter/viewfgmimage',
            data: {lastactivatedpanel:lastactivatedpanel, threshindex:threshindex, clusterchannelindex:clusterchannelindex,
                minimumdistance:minimumdistance, checkbox:checkbox},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    $('#PerformAnalysis').click(function(){

        if ($('#panel1').hasClass('active')) {
            var currentactivatedpanel = '1'
        }
        else if ($('#panel2').hasClass('active')) {
            var currentactivatedpanel = '2'
        }
        else{
            alert('Neither foreground panels are active')
        }
        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var bgindex = $('#bgindex').val();
        var fgindexdtthresh = $('#disttransthresh').val();
        var fgindexdterosion = $('#disttranserosion').val();
        var minimumdistance = $('#minimumdistance').val();
        var analysisoption = $('input[name="myAN"]:checked').val();

        $.ajax({
            url: '/clustercounter/performanalysis',
            data: {currentactivatedpanel:currentactivatedpanel,
                    threshindex:threshindex,
                    clusterchannelindex:clusterchannelindex,
                    bgindex:bgindex,
                    fgindexdtthresh:fgindexdtthresh,
                    fgindexdterosion:fgindexdterosion,
                    minimumdistance:minimumdistance,
                    checkbox:checkbox,
                    analysisoption:analysisoption},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
            }
        })
    })
    $('#PerformAdd').click(function(){

        if ($('#panel1').hasClass('active')) {
            var currentactivatedpanel = '1'
        }
        else if ($('#panel2').hasClass('active')) {
            var currentactivatedpanel = '2'
        }
        else{
            alert('Neither foreground panels are active')
        }
        if ($('#threshcheck').is(":checked")){
            var checkbox = '1'
        } else {
            var checkbox = '0'
        }
        var threshindex = $('#myRange').val();
        var clusterchannelindex = $('input[name="myRadio"]:checked').val();
        var bgindex = $('#bgindex').val();
        var fgindexdtthresh = $('#disttransthresh').val();
        var fgindexdterosion = $('#disttranserosion').val();
        var minimumdistance = $('#minimumdistance').val();
        var pxµm = $('#pxµminput').val();
        var analysisoption = $('input[name="myAN"]:checked').val();

        $.ajax({
            url: '/clustercounter/performadd',
            data: {currentactivatedpanel:currentactivatedpanel,
                    threshindex:threshindex,
                    clusterchannelindex:clusterchannelindex,
                    bgindex:bgindex,
                    fgindexdtthresh:fgindexdtthresh,
                    fgindexdterosion:fgindexdterosion,
                    minimumdistance:minimumdistance,
                    checkbox:checkbox,
                    pxµm:pxµm,
                    analysisoption:analysisoption},
            type: 'GET',
            contentType: "image/jpeg",
            success: function(result) {
                document.getElementById('selectedimg').src = 'data:image/jpeg;base64,'+ result;
                $('#PerformAdd').addClass('success')
                    setTimeout(function () {
                        $('#PerformAdd').removeClass('success');
                    }, 4000);
            }
        })
    })
    $('#clearresults').click(function(){

        $.ajax({
            url: '/clustercounter/clearresults',
            success: function(result) {
                $('#clearresults').addClass('success')
                    setTimeout(function () {
                        $('#clearresults').removeClass('success');
                    }, 4000);
            }
        })
    })
     $('#downloadresults').click(function(){

        $.ajax({
            url: '/clustercounter/downloadresults',
        })
    })
    $('#viewcurrentfiles').click(function(){
        $('#currentfiles').addClass('active');
        $('#currentfileslist').empty()
        $.ajax({
            url: '/clustercounter/getcurrentfilelist',
            type: 'GET',
            success: function(results) {
                let currentfileslist = JSON.parse(results)
                for (index = 0; index < currentfileslist.length; ++index) {
                    var listdata = currentfileslist[index]
                    $('#currentfileslist').append("<li class='listitem'>" + listdata + "</li>")
                }

            }
        })
    })
});

$(function() {

    $('.anoptionslabel').on('click', function() {
        $('.anoptionslabel.active').removeClass('active');
        $(this).addClass('active');

        //figure out which panel to show
        var panelToShow = $(this).attr('rel');

        //hide current panel
        // $('.fgpanel.active').slideUp(300, showNextPanel);

        if (panelToShow == 'panel2') {
            $("#thresholdselect").addClass('inactive')
            $("#bgselect").addClass('inactive')
            $("#fgselect").addClass('inactive')
            $(".ROIselect").addClass('inactive')
        }
        if (panelToShow == 'panel1') {
            $("#thresholdselect").removeClass('inactive')
            $("#bgselect").removeClass('inactive')
            $("#fgselect").removeClass('inactive')
            $(".ROIselect").removeClass('inactive')
        }
    });
});

$(function() {

    $('.fgoptionslabel').on('click', function() {
        $('.fgoptionslabel.active').removeClass('active');
        $(this).addClass('active');

        //figure out which panel to show
        var panelToShow = $(this).attr('rel');

        //hide current panel
        $('.fgpanel.active').slideUp(300, showNextPanel);

        //show next panel
        function showNextPanel() {
            $(this).removeClass('active');

            $('#'+panelToShow).slideDown(300, function() {
                $(this).addClass('active');
            });
        }
    });
});

// Close current files tab
$('.exittab').click(function () {
    $('#currentfiles').removeClass('active')
})

// Slider threshold
function rangeSlide(value){
        document.getElementById('rangeValue').innerHTML = value;
}

// Slider threshold
var slider = document.getElementById("myRange");
slider.addEventListener("mousemove", function(){rangeSlide(slider.value)});


// Slider distance transformation threshold
function rangeSlidedt(value){
        document.getElementById('disttransthreshvalue').innerHTML = value;
}

// Slider distance transformation threshold
var sliderdt = document.getElementById("disttransthresh");
sliderdt.addEventListener("mousemove", function(){rangeSlidedt(sliderdt.value)});


// Slider ROI
function rangeSlider(value){
        document.getElementById('ROIthresholdvalue').innerHTML = value;
}

// Slider ROI
var sliderr = document.getElementById("ROIthresholdslider");
sliderr.addEventListener("mousemove", function(){rangeSlider(sliderr.value)});

// Button upload czi file
var openfile = document.getElementById("open_file");
openfile.addEventListener("click", function(){document.getElementById('hiddenfileinput').click()});

document.getElementById("hiddenfileinput").onchange = function() {
    document.getElementById("file_submit").click();
}

$('#selectedimg').on('dragstart', function(event) { event.preventDefault(); });

$("#options1").hide();

$("#optionsbutton").click(function() {
    $("#options1").toggle(0);
})

// window close message
window.onbeforeunload = confirmExit;
function confirmExit() {
  return "You have attempted to leave this page.  If you have made any changes to the fields without clicking the Save button, your changes will be lost.  Are you sure you want to exit this page?";
}

$("#sessionID").html("Session ID: "+ user)