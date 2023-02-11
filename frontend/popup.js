function addVideos() {
    const videoCount = 3;
    for (let i = 0; i < videoCount; i++) {
        const link = document.createElement("a");
        link.href = "https://www.google.com/";
        link.target = "_blank";

        const thumbnail = document.createElement("img");
        thumbnail.src = "thumbnail.jpeg";
        thumbnail.classList.add("thumbnail");

        link.appendChild(thumbnail);


        const element = document.getElementById("videos");
        element.appendChild(link);
    }
}

function getRatings() {
    const testRatings = [2.7];
    const starsTotal = 5;
    const starsPercentage = testRatings[0] / starsTotal * 100;
    const starsPercentageRounded = `${Math.round((starsPercentage / 10) * 10)}%`;

    document.querySelector(".stars-inner").style.width = starsPercentageRounded;
}


getRatings();
addVideos();