// To disable the submit button of the form, once the button is pressed
// Prevents multiple submission by user
function formSubmit() {
    let submitBtn = document.getElementById("form-submit");
    submitBtn.disabled = true
}

function hasExtension(inputID, exts) {
    var fileName = document.getElementById(inputID).value;
    return (new RegExp('(' + exts.join('|').replace(/\./g, '\\.') + ')$')).test(fileName);
}

function fileUpload() {

    const fi = document.getElementById("file");

    if (fi.files.length > 1) {
        fi.value = "";
        alert("Only 1 file can be selected");
    }
    
    if (fi.files.length == 1) {

        const fsize = fi.files.item(0).size;
        const file = Math.round((fsize / 1024));
        if (file > 5120) {
            fi.value = "";
            alert("File size should be less than 5MB");
        }
        else if (!hasExtension("file", [".pdf"])) {
            fi.value = "";
            alert("Accepted format is .pdf only")
        }
    }

}