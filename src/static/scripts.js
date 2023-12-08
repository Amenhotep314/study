function startStudyTimer() {

    // https://stackoverflow.com/questions/5517597/plain-count-up-timer-in-javascript
    let studyStartTime = Math.floor(Date.now() / 1000);
    localStorage.setItem("studyStartTime", studyStartTime);
    updateStudyTimer();
}


function updateStudyTimer() {

    let now = Math.floor(Date.now() / 1000);
    let studyStartTime = localStorage.getItem("studyStartTime");
    let delta = now - studyStartTime;

    let hours = Math.floor(delta / 3600);
    let minutes = Math.floor(delta / 60) - (60*hours);
    var seconds = delta - (3600*hours) - (60*minutes);
    hours = addZeroes(hours);
    minutes = addZeroes(minutes);
    seconds = addZeroes(seconds);

    document.getElementById("studyTimer").innerHTML = hours + ":" + minutes + ":" + seconds;
    setTimeout(startTimeCounter, 500);
}


function addZeroes(i) {

    if(i < 10) {
        i = "0" + i;
    }

    return i;
}