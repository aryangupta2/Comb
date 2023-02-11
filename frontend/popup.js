document.addEventListener('DOMContentLoaded', ready)


function addVideos() {
    const videoCount = 3;
    for (let i = 0; i < videoCount; i++) {
        const link = document.createElement("a");
        link.href = "https://www.google.com/";
        link.target = "_blank";

        const thumbnail = document.createElement("img");
        thumbnail.src = "assets/thumbnail.jpeg";
        thumbnail.classList.add("thumbnail");

        link.appendChild(thumbnail);


        const element = document.getElementById("videos");
        element.appendChild(link);
    }
}

function getRatings() {
    const testRatings = [1.5, 3.8];

    const starsTotal = 5;
    let starsPercentage = (testRatings[0] / starsTotal) * 100;
    let starsPercentageRounded = `${Math.round((starsPercentage / 10) * 10)}%`;

    document.getElementById('1').style.width = starsPercentageRounded;

    starsPercentage = (testRatings[1] / starsTotal) * 100;
    starsPercentageRounded = `${Math.round((starsPercentage / 10) * 10)}%`;
    document.getElementById('2').style.width = starsPercentageRounded;
}


function ready() {
    getRatings();
    addVideos();
}