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

let resetButton = $("#resetButton");
let convertButton = $("#convertButton");
let cancelButton = $("#cancelButton")

let progress = $("#progress");
let statusMessage = $("#statusMessage");
let progressBar = $("#convertProgressBar");
let finishedMessage = $("#finished");
let errorMessage = $("#error");
let cancelMessage = $("#cancel");
let previewLink = $("#previewLink");
let downloadLink = $("#downloadLink");

let progressStream = null;
let currentJobId = "";

$(document).ready(function(e) {
    progress.hide();
    errorMessage.hide();
    cancelMessage.hide();
    finishedMessage.hide();
});

resetButton.click(function(e) {
    imageReduction.val("10");
    maxWidth.val("");
    maxHeight.val("");
    fontSize.val("10");
    spacing.val("1.1");
    characters.val(" .*:+%S0#@");
    frameFrequency.val("24");
});

convertButton.click(function(e) {
    let file = fileUpload[0].files[0];
    let formData = new FormData();
    formData.append("fileUpload", file);
    formData.append("imageReduction", imageReduction.val());
    formData.append("maxWidth", maxWidth.val());
    formData.append("maxHeight", maxHeight.val());
    formData.append("fontSize", fontSize.val());
    formData.append("spacing", spacing.val());
    formData.append("characters", characters.val());
    formData.append("frameFrequency", frameFrequency.val());
    
    showProgress();
    console.log("Converting...")

    fetch("/api/convert", {
        method: "POST",
        body: formData
    }).then(response => {
        console.log(response.status);
        if (response.status == 415) {
            showError("Uh oh, looks like we don't support that file format!");
            return "error";
        } else if (response.status == 413) {
            showError("This file is too large for us! Max size we take is 5 MB");
            return "error";
        }
        return response.json();
    }).then(data => {
        if (data != "error") {
            checkProgress(data);
            cancelButton.unbind("click");
            cancelButton.click(function() {
                cancelConversion(data);
            });
        }
    }).catch(error => {
        if (progressStream != null) {
            progressStream.close();
        }
        showError("Uh oh, something went wrong! Make sure your network is stable and the file size doesn't exceed 5MB!");
        // showError("Uh oh, something went wrong! Try again later?");
        console.log(error);
    })
});

function checkProgress(data) {
    progressStream = new SSE("/api/getprogress", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        payload: JSON.stringify(data)
    });
    progressStream.onmessage = function(event) {
        let data = JSON.parse(event.data);
        let status = data.status;
        if (status == "queued") {
            statusMessage.text("Queued. Waiting to start...");
        }
        if (status == "started") {
            let progress = parseFloat(data.progress).toFixed(2);
            statusMessage.text("Converting..." + progress + "%");
            progressBar.css("width", progress + "%");
        }
        if (status == "finished") {
            progressStream.close();
            let result = data.result;
            fetch("/api/getoutput", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(result)
            }).then(response => {
                return response.blob();
            }).then(file => {
                showFinished();
                let url = window.URL.createObjectURL(file);
                downloadLink.attr("download", fileUpload[0].files[0].name);
                downloadLink.attr("href", url);
                previewLink.attr("href", url);
                console.log("Success");
            }).catch(error => {
                showError("Uh oh, couldn't retrive file for some reason!");
                console.log("Error getting file");
            })
        }
    }
    progressStream.stream();
}

function cancelConversion(data) {
    progressStream.close();
    cancelMessage.text("Cancelling...");
    showCanceled();
    fetch("/api/cancel", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    }).then(response => {
        console.log("Cancelled");
        cancelMessage.text("Conversion cancelled!");
        allInputs.prop("disabled", false);
    }).catch(error => {
        showError();
        console.log(error);
    })
}

function showProgress() {
    allInputs.prop("disabled", true);
    statusMessage.text("Queuing...");
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

function showError(message = "Uh oh, something went wrong! Try again later maybe?") {
    allInputs.prop("disabled", false);
    progress.hide();
    errorMessage.show();
    errorMessage.text(message);
    cancelMessage.hide();
}

function showCanceled() {
    progress.hide();
    cancelMessage.show();
}