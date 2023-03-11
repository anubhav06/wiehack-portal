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
        else if (!hasExtension("file", [".pptx"])) {
            fi.value = "";
            alert("Accepted format is .pptx only")
        }
    }

}

// Countdown timer
document.addEventListener('DOMContentLoaded', function () {

    const second = 1000,
        minute = second * 60,
        hour = minute * 60,
        day = hour * 24;
    
    const endTime = JSON.parse(document.getElementById("roundEndTime")?.textContent);

    if (endTime == "") {
        document.getElementById("headline-local").style.display = "none";
        document.getElementById("countdown-local").style.display = "none";
    }
    
    const countDown = new Date(endTime).getTime();
    const x = setInterval(function () {

        const now = new Date().getTime()
        const distance = countDown - now;

        document.getElementById("days").innerText = Math.floor(distance / (day)),
        document.getElementById("hours").innerText = Math.floor((distance % (day)) / (hour)),
        document.getElementById("minutes").innerText = Math.floor((distance % (hour)) / (minute)),
        document.getElementById("seconds").innerText = Math.floor((distance % (minute)) / second);

        // Reload when 1 sec is left
        if (distance < 1000 && distance > -1000) {
            location.reload();
        }

        //do something later when date is reached
        if (distance < 0) {
            document.getElementById("headline-local").innerText = "Round Over!";
            document.getElementById("countdown-local").style.display = "none";
            clearInterval(x);
        }

        //seconds
    }, 1000);
})
