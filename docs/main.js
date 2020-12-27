// just some formatting to add a thicker underline to links
$("a").each((i, a) => {
    $(a).hover(() => {
        $(a).children("u").css("border-bottom", "0.15em white solid")
    }, () => {
        $(a).children("u").css("border-bottom", "none")
    })
});

let allInputs = $("#convert input");
let fileUpload = $("#fileUpload");
let imageReduction = $("#imageReduction");
let maxWidth = $("#maxWidth");
let maxHeight = $("#maxHeight");
let fontSize = $("#fontSize");
let spacing = $("#spacing");
let characters = $("#characters");
let frameFrequency = $("#frameFrequency");
let progress = $("#progress");
let finishedMessage = $("#finished");
let errorMessage = $("#error");
let downloadLink = $("#downloadLink");

$("#resetButton").click(() => {
    imageReduction.val("100");
    maxWidth.val("");
    maxHeight.val("");
    fontSize.val("10");
    spacing.val("1.1");
    characters.val(" .*:+%S0#@");
    frameFrequency.val("24");
});


$("#convertButton").click(() => {
    let formData = new FormData();
    formData.append("fileUpload", fileUpload[0].files[0]);
    formData.append("imageReduction", imageReduction.val());
    formData.append("maxWidth", maxWidth.val());
    formData.append("maxHeight", maxHeight.val());
    formData.append("fontSize", fontSize.val());
    formData.append("spacing", spacing.val());
    formData.append("characters", characters.val());
    formData.append("frameFrequency", frameFrequency.val());
    
    allInputs.prop("disabled", true);
    progress.show();
    errorMessage.hide();
    finishedMessage.hide();
    console.log("Converting...")

    fetch("http://localhost:5000/api/convertimage", {
        method: "POST",
        body: formData
    }).then(response => {
        return response.blob();
    }).then(file => {
        progress.hide();
        finishedMessage.show();
        downloadLink.download = "converted.txt.jpg";
        downloadLink.attr("href", window.URL.createObjectURL(file));
        allInputs.prop("disabled", false);
        console.log("Success")
    }).catch(error => {
        progress.hide();
        errorMessage.show();
        allInputs.prop("disabled", false);
        console.log("Uh oh something went wrong");
        console.log(error);
    })
});