function startStudyTimer() {

    // https://stackoverflow.com/questions/5517597/plain-count-up-timer-in-javascript
    let studyStartTime = Math.floor(Date.now() / 1000);
    localStorage.setItem("studyStartTime", studyStartTime);
    console.log("Started timer.");
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

    $("#studyTimer").html(hours + ":" + minutes + ":" + seconds);
    setTimeout(updateStudyTimer, 500);
}


function addZeroes(i) {

    if(i < 10) {
        i = "0" + i;
    }

    return i;
}

let weeklySummaryChart = null;
let weeklySummaryPosition = 0;

async function incrementWeeklySummaryChart(nextWeek) {

    if (nextWeek) {
        weeklySummaryPosition += 1;
    } else {
        weeklySummaryPosition -= 1;
    }
    renderWeeklySummaryChart()
}

async function renderWeeklySummaryChart() {

    if (weeklySummaryChart) {
        console.log(weeklySummaryChart);
        weeklySummaryChart.destroy();
    }
    weeklySummaryChart = await renderChart("weekly_summary", weeklySummaryPosition);
}

async function renderChart(id, arg) {

    const ctx = document.getElementById(id);
    const data = await fetch($SCRIPT_ROOT + "/" + id + "/" + arg).then(response => response.json());
    console.log("Built chart", id);
    let chart = new Chart(ctx, data);
    return chart;
}


async function checkNotifications() {
    const notification = await fetch($SCRIPT_ROOT + "/check_notifications").then(response => response.json());
    let notificationText = document.getElementById("notification-text");
    let notificationBanner = document.getElementById("notification-banner");

    if(notification == "") {
        notificationBanner.style.display = "none";
    } else {
        notificationBanner.style.display = "inline-block";
        notificationText.innerHTML = notification;
        console.log("Retrieved notifications", notification);
    }
}