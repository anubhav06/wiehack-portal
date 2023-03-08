// To disable the submit button of the form, once the button is pressed
// Prevents multiple submission by user
function formSubmit() {
    let submitBtn = document.getElementById("form-submit");
    submitBtn.disabled = true
}

// Countdown timer
document.addEventListener('DOMContentLoaded', function () {
    
    const second = 1000,
        minute = second * 60,
        hour = minute * 60,
        day = hour * 24;
    
    const endTime = JSON.parse(document.getElementById("roundEndTime").textContent);
  
    const countDown = new Date(endTime).getTime(),
      x = setInterval(function() {    

        const now = new Date().getTime(),
              distance = countDown - now;

        document.getElementById("days").innerText = Math.floor(distance / (day)),
        document.getElementById("hours").innerText = Math.floor((distance % (day)) / (hour)),
        document.getElementById("minutes").innerText = Math.floor((distance % (hour)) / (minute)),
        document.getElementById("seconds").innerText = Math.floor((distance % (minute)) / second);

        //do something later when date is reached
        if (distance < 0) {
            document.getElementById("headline-local").innerText = "Round Over!";
            document.getElementById("countdown-local").style.display = "none";
            clearInterval(x);
            location.reload();
        }
        //seconds
      }, 0)
})
