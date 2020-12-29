// add a thicker underline to links when hovering
$("a").each((i, a) => {
    $(a).hover(() => {
        $(a).children("u").css("border-bottom", "0.15em white solid")
    }, () => {
        $(a).children("u").css("border-bottom", "none")
    })
});

// offset scroll to element id anchor
$(".scrollToLink").click(function(e) {
    e.preventDefault();
    let target = $(this).attr("href");
    let offset = 100;
    $("html, body").stop().animate({
        "scrollTop": $(target).offset().top - offset
    }, 50);
})

let allInputs = $("#convert input, #convert button:not(#cancelButton)");
let fileUpload = $("#fileUpload");
let imageReduction = $("#imageReduction");
let maxWidth = $("#maxWidth");
let maxHeight = $("#maxHeight");
let fontSize = $("#fontSize");
let spacing = $("#spacing");
let characters = $("#characters");
let frameFrequency = $("#frameFrequency");

let progress = $("#progress");
let statusMessage = $("#statusMessage");
let progressBar = $("#convertProgressBar");
let finishedMessage = $("#finished");
let errorMessage = $("#error");
let cancelMessage = $("#cancel");
let previewLink = $("#previewLink");
let downloadLink = $("#downloadLink");

let conversionProgress = null;
let currentJobId = ""

$(document).ready(function(e) {
    progress.hide();
    errorMessage.hide();
    cancelMessage.hide();
    finishedMessage.hide();
});

$("#resetButton").click(function(e) {
    imageReduction.val("10");
    maxWidth.val("");
    maxHeight.val("");
    fontSize.val("10");
    spacing.val("1.1");
    characters.val(" .*:+%S0#@");
    frameFrequency.val("24");
});

$("#convertButton").click(function(e) {
    let formData = new FormData();
    formData.append("fileUpload", fileUpload[0].files[0]);
    formData.append("imageReduction", imageReduction.val());
    formData.append("maxWidth", maxWidth.val());
    formData.append("maxHeight", maxHeight.val());
    formData.append("fontSize", fontSize.val());
    formData.append("spacing", spacing.val());
    formData.append("characters", characters.val());
    formData.append("frameFrequency", frameFrequency.val());
    
    showProgress();
    console.log("Converting...")

    // conversionProgress = setInterval(checkProgress, 2000);

    fetch("http://0.0.0.0:5000/api/convert", {
        method: "POST",
        body: formData
    }).then(response => {
        return response.json();
    }).then(data => {
        currentJobId = data;
        convertProgress = setInterval(checkProgress, 1000);
    }).catch(error => {
        showError();
        clearInterval(convertProgress);
    })
});

function checkProgress() {
    fetch("http://0.0.0.0:5000/api/getprogress", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(currentJobId)
    }).then(response => {
        const contentType = response.headers.get("Content-Type");
        if (contentType.includes("application/json")) {
            response.json().then(data => {
                let progress = Math.round(parseFloat(data) * 10) / 10;
                statusMessage.text("Converting..." + progress + "%");
                progressBar.css("width", data + "%")
            })
        } else {
            response.blob().then((file) => {
                clearInterval(convertProgress);
                showFinished();
                let url = window.URL.createObjectURL(file);
                downloadLink.attr("download", fileUpload[0].files[0].name);
                downloadLink.attr("href", url);
                previewLink.attr("href", url);
                console.log("Success")
            })
        }
    }).catch(error => {
        showError();
        clearInterval(convertProgress);
    })
}

$("#cancelButton").click(function(e) {
    cancelMessage.text("Cancelling...");
    showCanceled();
    clearInterval(convertProgress);
    fetch("http://0.0.0.0:5000/api/cancel", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(currentJobId)
    }).then(response => {
        cancelMessage.text("Conversion cancelled!");
        allInputs.prop("disabled", false);
    }).catch(error => {
        showError();
    })
});

function showProgress() {
    allInputs.prop("disabled", true);
    statusMessage.text("Converting...");
    progressBar.css("width", "0%");
    progress.show();
    errorMessage.hide();
    cancelMessage.hide();
    finishedMessage.hide();
}

function showFinished() {
    allInputs.prop("disabled", false);
    progress.hide();
    finishedMessage.show();
}

function showError() {
    allInputs.prop("disabled", false);
    progress.hide();
    errorMessage.show();
    cancelMessage.hide();
}

function showCanceled() {
    progress.hide();
    cancelMessage.show();
}