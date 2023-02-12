main()
/*
const data = {
    "stores": [
        {
            "site": "amazon",
            "reviews": [
                {
                    "title": "GOOD AS NEW!",
                    "link": "https://www.amazon.com/gp/customer-reviews/R1IWWDMQ318GSX/ref=cm_cr_arp_d_viewpnt?ie=UTF8&ASIN=B07H6QCGGZ#R1IWWDMQ318GSX",
                    "rating": 5.0
                },
                {
                    "title": "Right airpod low",
                    "link": "https://www.amazon.com/gp/customer-reviews/R31T9L17S6ILGW/ref=cm_cr_arp_d_viewpnt?ie=UTF8&ASIN=B07H6QCGGZ#R31T9L17S6ILGW",
                    "rating": 3.0
                }
            ],
            "rating": 4.2
        }
    ],
    "articles": [
        {
            "site": "toms-guide",
            "link": "https://www.tomsguide.com/us/bose-soundsport-in-ear,review-2696.html",
            "rating": 3.0
        }
    ],
    "videos": [
        {
            "link": "https://www.youtube.com/watch?v=_d6sXfMmKV4",
            "thumbnail_url": "https://i.ytimg.com/vi/_d6sXfMmKV4/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBVavX8HRs9AcQU9d_xtpZUtNIgQA"
        },
        {
            "link": "https://www.youtube.com/watch?v=ZTE5iC0EZzw",
            "thumbnail_url": "https://i.ytimg.com/vi/ZTE5iC0EZzw/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLASHePogPMod6NRXKEfoPJO1SmdzQ"
        },
        {
            "link": "https://www.youtube.com/watch?v=jkUMblxVV5c",
            "thumbnail_url": "https://i.ytimg.com/vi/jkUMblxVV5c/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCVkYDbEXCzpy-PicowQizc9V1PTw"
        },
        {
            "link": "https://www.youtube.com/watch?v=f3DfJxvkN-8",
            "thumbnail_url": "https://i.ytimg.com/vi/f3DfJxvkN-8/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBFLJqzGNscyl-p54101-YGih8W9g"
        },
        {
            "link": "https://www.youtube.com/watch?v=khxwPHj-j2s",
            "thumbnail_url": "https://i.ytimg.com/vi/khxwPHj-j2s/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLApHROKw1zYOv0_HFsOwdL56vAohQ"
        }
    ],
    "article_average": 3.0,
    "customer_average": 4.2
}
*/

function displayVideos(data) {
    const info = data['videos'];
    for (let video in info) {
        const container = document.createElement('div');
        container.classList.add('video-container')
    

        const link = document.createElement('a');
        link.href = info[video]['link'];
        link.target = '_blank';
    
        const thumbnail = document.createElement('img');
        thumbnail.src =  info[video]['thumbnail_url'];
        thumbnail.classList.add('thumbnail');

        link.appendChild(thumbnail)

        container.appendChild(link);
        document.getElementById('videos').appendChild(container)
    }
}

async function getData(url='') {
    const data = "Apple AirPods (2nd generation) In-Ear Truly Wireless Headphones - White"
    const endpoint = 'preloaded' // 'ratings'
    const baseURL = `http://localhost:8000/${endpoint}/?product_name=`
    const response = await fetch(baseURL + data, {
        method: 'GET', 
        mode: 'cors',
        cache: 'no-cache', 
        credentials: 'same-origin', 
        headers: {
          'Content-Type': 'application/json',
          "Access-Control-Allow-Origin": "*"
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
      }).then((response) => response.json());
      return response;
}

function updateHome(data) {
    window.localStorage.setItem('productData', JSON.stringify(data));
    console.log(data);
}


function displayRatings(data) {
    let articleRating = data['article_average'];
    const starsTotal = 5;
    let starsPercentage = articleRating / starsTotal * 100;
    let starsPercentageRounded = `${Math.round((starsPercentage / 10) * 10)}%`;
    document.getElementById("1").style.width = starsPercentageRounded;

    const customerRating = data['customer_average'];
    starsPercentage = customerRating / starsTotal * 100;
    starsPercentageRounded = `${Math.round((starsPercentage / 10) * 10)}%`;
    document.getElementById("2").style.width = starsPercentageRounded;
}


function enableLoading() {
    document.getElementById('top').style.display = 'none';
    const loading = document.createElement('img');
    loading.src = 'assets/comb_logo.png';
    loading.setAttribute('id', 'loading');
    loading.classList += 'animate-flicker'
    document.body.appendChild(loading)
}

function disableLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('top').style.display = 'inline-block';
}


async function main() {
    
    let storageData = localStorage.getItem("data")
    
    if (storageData === null) {
        
        enableLoading()
        const data = await getData();
        localStorage.setItem("data", JSON.stringify(data));
        disableLoading()
        displayRatings(data);
        displayVideos(data);
        
    } else {
        storageData = JSON.parse(storageData)
        displayRatings(storageData);
        displayVideos(storageData);
    }
    
}