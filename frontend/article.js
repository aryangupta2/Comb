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

function displayArticleReviews() {
    let data = JSON.parse(localStorage.getItem("data"))
    const info = data['articles'];
    for (let site in info) {
        const container = document.createElement('div');
        container.classList.add('review-container')

        const infoContainer = document.createElement('div');
        infoContainer.classList.add('info-container');
    
        const title = document.createElement('h2');
        const titleText = document.createTextNode(info[site]['site']);
        console.log(info[site]['site']);
        title.appendChild(titleText);
        title.classList.add('review-title');
        infoContainer.appendChild(title);

        const rating = document.createElement('h3');
        const ratingText = document.createTextNode(`${info[site]['rating']}/5`);
        rating.appendChild(ratingText);
        title.classList.add('review-rating');
        infoContainer.appendChild(rating);

        const link = document.createElement('a');
        link.href = info[site]['link'];
        link.target = '_blank';
    
        const companyLogo = document.createElement('img');
        companyLogo.src =  `assets/${info[site]['site']}_logo.jpg`;
        companyLogo.classList.add('company-logo');

        link.appendChild(companyLogo)

        container.appendChild(link)
        container.append(infoContainer)
        document.body.appendChild(container)
    }
}

function main() {
    displayArticleReviews();
}